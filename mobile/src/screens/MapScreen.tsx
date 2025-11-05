import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ActivityIndicator,
  Text,
  Platform,
  ScrollView,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import { api } from '../services/api';
import AdvancedFilterModal from '../components/AdvancedFilterModal';

const isWeb = Platform.OS === 'web';

// 웹용 간단한 지도 표시 컴포넌트
function WebMapView({ missingPersons }) {
  const missingCount = missingPersons.filter((p) => p.status === 'missing').length;
  const resolvedCount = missingPersons.filter((p) => p.status === 'resolved').length;

  return (
    <ScrollView style={styles.webMapContainer}>
      <View style={styles.webMapHeader}>
        <Text style={styles.webMapTitle}>🗺️ 실종 사건 위치</Text>
        <Text style={styles.webMapSubtitle}>
          모바일 앱에서 실제 지도로 확인하세요
        </Text>
        <View style={styles.statusSummary}>
          <Text style={styles.statusMissing}>🔴 실종 중: {missingCount}명</Text>
          <Text style={styles.statusResolved}>🟢 실종 해제: {resolvedCount}명</Text>
        </View>
      </View>

      <View style={styles.locationGrid}>
        {missingPersons.map((person, index) => {
          const isResolved = person.status === 'resolved';
          const cardColor = isResolved ? '#4CAF50' : '#FF3B30';
          const emoji = isResolved ? '✅' : '📍';

          return (
            <View
              key={person.id}
              style={[styles.locationCard, { borderLeftColor: cardColor }]}
            >
              <View style={[styles.locationNumber, { backgroundColor: cardColor }]}>
                <Text style={styles.locationNumberText}>{index + 1}</Text>
              </View>
              <View style={styles.locationInfo}>
                <Text style={styles.locationAddress}>
                  {emoji} {person.location_address}
                </Text>
                <Text style={styles.locationDate}>
                  실종: {new Date(person.missing_date).toLocaleDateString('ko-KR')}
                </Text>
                {person.age && person.gender && (
                  <Text style={styles.personInfo}>
                    {person.gender === 'M' ? '남성' : '여성'} · {person.age}세
                  </Text>
                )}
                {isResolved && person.resolved_at && (
                  <Text style={styles.resolvedDate}>
                    해제: {new Date(person.resolved_at).toLocaleDateString('ko-KR')} 🎉
                  </Text>
                )}
                {person.latitude && person.longitude && (
                  <Text style={styles.locationCoords}>
                    위도: {person.latitude.toFixed(4)}, 경도: {person.longitude.toFixed(4)}
                  </Text>
                )}
              </View>
            </View>
          );
        })}
      </View>
    </ScrollView>
  );
}

// 모바일용 실제 지도 컴포넌트
function MobileMapView({ missingPersons }) {
  // react-native-maps를 동적으로 import하려고 시도
  let MapView, Marker, Callout;

  try {
    const maps = require('react-native-maps');
    MapView = maps.default;
    Marker = maps.Marker;
    Callout = maps.Callout;
  } catch (e) {
    // react-native-maps가 설치되지 않은 경우
    return (
      <View style={styles.centered}>
        <Text style={styles.installText}>📦 지도 기능 설치 필요</Text>
        <Text style={styles.installSubtext}>
          다음 명령어를 실행하세요:{'\n\n'}
          npx expo install react-native-maps
        </Text>
      </View>
    );
  }

  // 지도 중심 계산 (위도/경도가 있는 실종자들의 평균)
  const validPersons = missingPersons.filter(
    (p) => p.latitude && p.longitude
  );

  if (validPersons.length === 0) {
    return (
      <View style={styles.centered}>
        <Text style={styles.emptyText}>위치 정보가 있는 데이터가 없습니다</Text>
      </View>
    );
  }

  const avgLat =
    validPersons.reduce((sum, p) => sum + p.latitude, 0) / validPersons.length;
  const avgLng =
    validPersons.reduce((sum, p) => sum + p.longitude, 0) / validPersons.length;

  return (
    <MapView
      style={styles.map}
      initialRegion={{
        latitude: avgLat,
        longitude: avgLng,
        latitudeDelta: 2.0,
        longitudeDelta: 2.0,
      }}
    >
      {validPersons.map((person) => {
        const isMissing = person.status === 'missing';
        const pinColor = isMissing ? '#FF3B30' : '#34C759';

        return (
          <Marker
            key={person.id}
            coordinate={{
              latitude: person.latitude,
              longitude: person.longitude,
            }}
            pinColor={pinColor}
            title={person.location_address}
          >
            <Callout style={styles.callout}>
              <View style={styles.calloutContent}>
                <Text style={styles.calloutTitle}>
                  {isMissing ? '🔴 실종 중' : '🟢 실종 해제'}
                </Text>
                <Text style={styles.calloutAddress}>{person.location_address}</Text>
                <Text style={styles.calloutDate}>
                  실종: {new Date(person.missing_date).toLocaleDateString('ko-KR')}
                </Text>
                {person.age && person.gender && (
                  <Text style={styles.calloutInfo}>
                    {person.gender === 'M' ? '남성' : '여성'} · {person.age}세
                  </Text>
                )}
                {!isMissing && person.resolved_at && (
                  <Text style={styles.calloutResolved}>
                    해제: {new Date(person.resolved_at).toLocaleDateString('ko-KR')}
                  </Text>
                )}
              </View>
            </Callout>
          </Marker>
        );
      })}
    </MapView>
  );
}

export default function MapScreen() {
  const [missingPersons, setMissingPersons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [activeTab, setActiveTab] = useState<'all' | 'missing' | 'resolved'>('all');
  const [showAdvancedFilter, setShowAdvancedFilter] = useState(false);
  const [advancedFilters, setAdvancedFilters] = useState<any>({});

  // 데이터 로드 함수
  const loadData = async (status = 'all', filters = {}) => {
    try {
      setLoading(true);
      const params: any = {
        limit: 500, // 지도에서는 더 많은 데이터 표시
        status: status === 'all' ? undefined : status,
      };

      // 고급 필터 적용
      if (filters.startDate && filters.endDate) {
        params.start_date = filters.startDate;
        params.end_date = filters.endDate;
      }
      if (filters.gender) {
        params.gender = filters.gender;
      }
      if (filters.ageMin !== undefined) {
        params.age_min = filters.ageMin;
      }
      if (filters.ageMax !== undefined) {
        params.age_max = filters.ageMax;
      }
      if (filters.hasDisability !== undefined) {
        params.has_disability = filters.hasDisability;
      }

      const data = await api.getMissingPersons(params);
      const items = data.items || data;
      setMissingPersons(items);
    } catch (error) {
      console.error('Error loading data:', error);
      setErrorMsg('데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(activeTab, advancedFilters);
  }, [activeTab, advancedFilters]);

  const handleAdvancedFilterApply = (filters) => {
    setAdvancedFilters(filters);
  };

  const activeFilterCount = Object.keys(advancedFilters).filter(
    (key) => advancedFilters[key] !== undefined && advancedFilters[key] !== null
  ).length;

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>지도 로딩 중...</Text>
      </View>
    );
  }

  if (errorMsg) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>{errorMsg}</Text>
      </View>
    );
  }

  const missingCount = missingPersons.filter((p) => p.status === 'missing').length;
  const resolvedCount = missingPersons.filter((p) => p.status === 'resolved').length;
  const withLocationCount = missingPersons.filter(
    (p) => p.latitude && p.longitude
  ).length;

  return (
    <View style={styles.container}>
      {/* 탭 메뉴 */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'all' && styles.tabActive]}
          onPress={() => setActiveTab('all')}
        >
          <Text style={[styles.tabText, activeTab === 'all' && styles.tabTextActive]}>
            전체
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'missing' && styles.tabActive]}
          onPress={() => setActiveTab('missing')}
        >
          <Text style={[styles.tabText, activeTab === 'missing' && styles.tabTextActive]}>
            실종 중
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'resolved' && styles.tabActive]}
          onPress={() => setActiveTab('resolved')}
        >
          <Text style={[styles.tabText, activeTab === 'resolved' && styles.tabTextActive]}>
            실종 해제
          </Text>
        </TouchableOpacity>
      </View>

      {/* 필터 버튼 */}
      <TouchableOpacity
        style={styles.filterButton}
        onPress={() => setShowAdvancedFilter(true)}
      >
        <Text style={styles.filterIcon}>⚙️</Text>
        <Text style={styles.filterText}>
          고급 필터{activeFilterCount > 0 && ` (${activeFilterCount})`}
        </Text>
      </TouchableOpacity>

      {/* 통계 오버레이 */}
      <View style={styles.statsOverlay}>
        <Text style={styles.statsText}>
          📍 전체 {missingPersons.length}건 · 위치 정보 {withLocationCount}건
        </Text>
        <View style={styles.statsRow}>
          <Text style={styles.statsMissing}>🔴 실종 중: {missingCount}</Text>
          <Text style={styles.statsResolved}>🟢 해제: {resolvedCount}</Text>
        </View>
      </View>

      {/* 지도 또는 리스트 */}
      {missingPersons.length > 0 ? (
        isWeb ? (
          <WebMapView missingPersons={missingPersons} />
        ) : (
          <MobileMapView missingPersons={missingPersons} />
        )
      ) : (
        <View style={styles.centered}>
          <Text style={styles.emptyText}>표시할 데이터가 없습니다</Text>
          <Text style={styles.emptySubtext}>
            필터 조건을 변경하거나{'\n'}백엔드에서 데이터를 추가해주세요
          </Text>
        </View>
      )}

      {/* 고급 필터 모달 */}
      <AdvancedFilterModal
        visible={showAdvancedFilter}
        onClose={() => setShowAdvancedFilter(false)}
        onApply={handleAdvancedFilterApply}
        initialFilters={advancedFilters}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 20,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  errorText: {
    fontSize: 16,
    color: '#FF3B30',
    textAlign: 'center',
    paddingHorizontal: 20,
  },

  // 탭
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  tabActive: {
    borderBottomColor: '#007AFF',
  },
  tabText: {
    fontSize: 15,
    fontWeight: '500',
    color: '#8E8E93',
  },
  tabTextActive: {
    color: '#007AFF',
    fontWeight: '600',
  },

  // 필터 버튼
  filterButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    paddingHorizontal: 16,
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E5E5EA',
  },
  filterIcon: {
    fontSize: 14,
    marginRight: 6,
  },
  filterText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#007AFF',
  },

  // 통계
  statsOverlay: {
    backgroundColor: '#007AFF',
    padding: 12,
    alignItems: 'center',
  },
  statsText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 4,
  },
  statsRow: {
    flexDirection: 'row',
    gap: 16,
  },
  statsMissing: {
    fontSize: 13,
    fontWeight: '600',
    color: '#FFCCCB',
  },
  statsResolved: {
    fontSize: 13,
    fontWeight: '600',
    color: '#C8E6C9',
  },

  // 지도
  map: {
    flex: 1,
    width: '100%',
    height: '100%',
  },

  // 마커 Callout
  callout: {
    width: 200,
    padding: 0,
  },
  calloutContent: {
    padding: 10,
  },
  calloutTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 6,
  },
  calloutAddress: {
    fontSize: 13,
    fontWeight: '500',
    color: '#333',
    marginBottom: 4,
  },
  calloutDate: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  calloutInfo: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  calloutResolved: {
    fontSize: 12,
    color: '#34C759',
    fontWeight: '600',
    marginTop: 4,
  },

  // 웹 지도
  webMapContainer: {
    flex: 1,
  },
  webMapHeader: {
    backgroundColor: '#E3F2FD',
    padding: 20,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: '#2196F3',
  },
  webMapTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1565C0',
    marginBottom: 8,
  },
  webMapSubtitle: {
    fontSize: 14,
    color: '#1976D2',
  },
  statusSummary: {
    flexDirection: 'row',
    gap: 15,
    marginTop: 12,
  },
  statusMissing: {
    fontSize: 14,
    fontWeight: '600',
    color: '#C62828',
  },
  statusResolved: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2E7D32',
  },
  locationGrid: {
    padding: 15,
  },
  locationCard: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
    borderLeftWidth: 4,
  },
  locationNumber: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  locationNumberText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  locationInfo: {
    flex: 1,
  },
  locationAddress: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 6,
  },
  locationDate: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  personInfo: {
    fontSize: 13,
    color: '#666',
    marginBottom: 4,
  },
  resolvedDate: {
    fontSize: 14,
    color: '#4CAF50',
    fontWeight: '600',
    marginBottom: 4,
  },
  locationCoords: {
    fontSize: 12,
    color: '#999',
  },
  emptyText: {
    fontSize: 18,
    color: '#666',
    fontWeight: '600',
    marginBottom: 8,
    textAlign: 'center',
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    lineHeight: 20,
  },
  installText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  installSubtext: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    lineHeight: 22,
  },
});
