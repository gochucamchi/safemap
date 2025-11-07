import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { api } from '../services/api';
import DateFilter from '../components/DateFilter';
import AdvancedFilterModal from '../components/AdvancedFilterModal';
import DetailModal from '../components/DetailModal';
import { useAuth } from '../contexts/AuthContext';

export default function ListScreen() {
  const { isAuthenticated } = useAuth();
  const [missingPersons, setMissingPersons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedDays, setSelectedDays] = useState(30);
  const [activeTab, setActiveTab] = useState<'all' | 'missing' | 'resolved' | 'location_unknown'>('all');
  const [showAdvancedFilter, setShowAdvancedFilter] = useState(false);
  const [advancedFilters, setAdvancedFilters] = useState<any>({});
  const [selectedPerson, setSelectedPerson] = useState<any>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  // 데이터 로드 (모든 필터 적용)
  const loadData = async (days = 30, status = 'all', filters = {}) => {
    try {
      const params: any = {
        limit: 100,
      };

      // 탭별 필터 적용
      if (status === 'all') {
        // 전체: status 필터 없음
        params.status = 'all';
      } else if (status === 'location_unknown') {
        // 위치 불명: geocoding_status가 failed인 것만
        params.geocoding_status = 'failed';
      } else {
        // missing 또는 resolved
        params.status = status;
      }

      // 날짜 필터: 고급 필터에서 직접 입력한 날짜가 있으면 우선 사용
      if (filters.startDate && filters.endDate) {
        params.start_date = filters.startDate;
        params.end_date = filters.endDate;
      } else if (days) {
        params.days = days;
      }

      // 성별 필터
      if (filters.gender) {
        params.gender = filters.gender;
      }

      // 나이 필터
      if (filters.ageMin !== undefined) {
        params.age_min = filters.ageMin;
      }
      if (filters.ageMax !== undefined) {
        params.age_max = filters.ageMax;
      }

      // 장애 필터
      if (filters.hasDisability !== undefined) {
        params.has_disability = filters.hasDisability;
      }

      const data = await api.getMissingPersons(params);
      
      // API 응답 형식 처리
      const items = data.items || data;
      
      // ✅ TypeScript 오류 수정: .getTime() 사용
      const sorted = items.sort((a, b) =>
        new Date(b.missing_date).getTime() - new Date(a.missing_date).getTime()
      );
      setMissingPersons(sorted);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // selectedDays, activeTab, advancedFilters가 변경되면 데이터 다시 로드
  useEffect(() => {
    loadData(selectedDays, activeTab, advancedFilters);
  }, [selectedDays, activeTab, advancedFilters]);

  // 날짜 필터 변경 핸들러
  const handleFilterChange = (days) => {
    setSelectedDays(days);
  };

  // 탭 변경 핸들러
  const handleTabChange = (tab: 'all' | 'missing' | 'resolved' | 'location_unknown') => {
    setActiveTab(tab);
  };

  // 고급 필터 적용 핸들러
  const handleAdvancedFilterApply = (filters) => {
    setAdvancedFilters(filters);
  };

  // 새로고침 핸들러
  const onRefresh = () => {
    setRefreshing(true);
    loadData(selectedDays, activeTab, advancedFilters);
  };

  // 리스트 아이템 렌더링
  const renderItem = ({ item }) => {
    const isMissing = item.status === 'missing';

    return (
      <TouchableOpacity
        style={styles.card}
        onPress={() => {
          setSelectedPerson(item);
          setShowDetailModal(true);
        }}
      >
        <View style={styles.cardHeader}>
          <Text style={styles.date}>
            {new Date(item.missing_date).toLocaleDateString('ko-KR', {
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </Text>
          <View style={[styles.badge, isMissing ? styles.missingBadge : styles.resolvedBadge]}>
            <Text style={styles.badgeText}>
              {isMissing ? '실종 중' : '실종 해제'}
            </Text>
          </View>
        </View>

        <View style={styles.cardBody}>
          <Text style={styles.location} numberOfLines={2}>
            📍 {item.location_address}
          </Text>

          {item.age_at_disappearance && item.gender && (
            <Text style={styles.info}>
              {item.gender === 'M' ? '남성' : '여성'} · {item.age_at_disappearance}세
            </Text>
          )}

          {item.location_detail && (
            <Text style={styles.detail} numberOfLines={2}>
              {item.location_detail}
            </Text>
          )}

          {!isMissing && item.resolved_at && (
            <Text style={styles.resolvedDate}>
              ✓ {new Date(item.resolved_at).toLocaleDateString('ko-KR')} 실종 해제
            </Text>
          )}
        </View>
      </TouchableOpacity>
    );
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  // 활성 필터 개수 계산
  const activeFilterCount = Object.keys(advancedFilters).filter(
    key => advancedFilters[key] !== undefined && advancedFilters[key] !== null
  ).length;

  return (
    <View style={styles.container}>
      {/* 탭 메뉴 */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'all' && styles.tabActive]}
          onPress={() => handleTabChange('all')}
        >
          <Text style={[styles.tabText, activeTab === 'all' && styles.tabTextActive]}>
            전체
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'missing' && styles.tabActive]}
          onPress={() => handleTabChange('missing')}
        >
          <Text style={[styles.tabText, activeTab === 'missing' && styles.tabTextActive]}>
            실종 중
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'resolved' && styles.tabActive]}
          onPress={() => handleTabChange('resolved')}
        >
          <Text style={[styles.tabText, activeTab === 'resolved' && styles.tabTextActive]}>
            실종 해제
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'location_unknown' && styles.tabActive]}
          onPress={() => handleTabChange('location_unknown')}
        >
          <Text style={[styles.tabText, activeTab === 'location_unknown' && styles.tabTextActive]}>
            위치 불명
          </Text>
        </TouchableOpacity>
      </View>

      {/* 필터 바 */}
      <View style={styles.filterBar}>
        <DateFilter
          onFilterChange={handleFilterChange}
          initialDays={30}
        />
        <TouchableOpacity
          style={styles.advancedFilterButton}
          onPress={() => setShowAdvancedFilter(true)}
        >
          <Text style={styles.advancedFilterIcon}>⚙️</Text>
          <Text style={styles.advancedFilterText}>
            고급 필터
            {activeFilterCount > 0 && ` (${activeFilterCount})`}
          </Text>
        </TouchableOpacity>
      </View>

      {/* 결과 개수 표시 */}
      {missingPersons.length > 0 && (
        <View style={styles.resultBar}>
          <Text style={styles.resultText}>
            총 {missingPersons.length}건
          </Text>
        </View>
      )}

      {missingPersons.length === 0 ? (
        <View style={styles.centered}>
          <Text style={styles.emptyText}>표시할 데이터가 없습니다</Text>
          <Text style={styles.emptySubtext}>
            선택한 기간에 데이터가 없거나{'\n'}
            백엔드 서버에서 데이터를 동기화해주세요
          </Text>
        </View>
      ) : (
        <FlatList
          data={missingPersons}
          renderItem={renderItem}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        />
      )}

      {/* 고급 필터 모달 */}
      <AdvancedFilterModal
        visible={showAdvancedFilter}
        onClose={() => setShowAdvancedFilter(false)}
        onApply={handleAdvancedFilterApply}
        initialFilters={advancedFilters}
      />

      {/* 상세 정보 모달 */}
      <DetailModal
        visible={showDetailModal}
        onClose={() => {
          setShowDetailModal(false);
          setSelectedPerson(null);
        }}
        person={selectedPerson}
        isAuthenticated={isAuthenticated}
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
  },
  // 필터 바
  filterBar: {
    backgroundColor: '#fff',
  },
  advancedFilterButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: '#F2F2F7',
    marginHorizontal: 16,
    marginVertical: 8,
    borderRadius: 8,
    gap: 8,
  },
  advancedFilterIcon: {
    fontSize: 16,
  },
  advancedFilterText: {
    fontSize: 15,
    fontWeight: '500',
    color: '#007AFF',
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
    paddingVertical: 14,
    paddingHorizontal: 4,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  tabActive: {
    borderBottomColor: '#007AFF',
  },
  tabText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#8E8E93',
  },
  tabTextActive: {
    color: '#007AFF',
    fontWeight: '600',
  },
  resultBar: {
    backgroundColor: '#fff',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  resultText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  listContent: {
    padding: 15,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  date: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  missingBadge: {
    backgroundColor: '#FF3B30',
  },
  resolvedBadge: {
    backgroundColor: '#34C759',
  },
  badgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  cardBody: {
    gap: 6,
  },
  location: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  info: {
    fontSize: 14,
    color: '#666',
  },
  detail: {
    fontSize: 14,
    color: '#999',
    lineHeight: 20,
  },
  resolvedDate: {
    fontSize: 13,
    color: '#34C759',
    fontWeight: '600',
    marginTop: 4,
  },
  emptyText: {
    fontSize: 18,
    color: '#666',
    fontWeight: '600',
    textAlign: 'center',
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    marginTop: 8,
    textAlign: 'center',
  },
});
