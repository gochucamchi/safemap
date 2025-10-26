import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Alert, ActivityIndicator, Text, Platform, ScrollView } from 'react-native';
import { api } from '../services/api';

// 웹인지 확인
const isWeb = Platform.OS === 'web';

// 웹용 간단한 지도 표시 컴포넌트
function WebMapView({ missingPersons }) {
  return (
    <ScrollView style={styles.webMapContainer}>
      <View style={styles.webMapHeader}>
        <Text style={styles.webMapTitle}>🗺️ 실종 사건 위치</Text>
        <Text style={styles.webMapSubtitle}>
          모바일 앱에서 실제 지도로 확인하세요
        </Text>
      </View>
      
      <View style={styles.locationGrid}>
        {missingPersons.map((person, index) => (
          <View key={person.id} style={styles.locationCard}>
            <View style={styles.locationNumber}>
              <Text style={styles.locationNumberText}>{index + 1}</Text>
            </View>
            <View style={styles.locationInfo}>
              <Text style={styles.locationAddress}>📍 {person.location_address}</Text>
              <Text style={styles.locationDate}>
                {new Date(person.missing_date).toLocaleDateString('ko-KR')}
              </Text>
              {person.latitude && person.longitude && (
                <Text style={styles.locationCoords}>
                  위도: {person.latitude.toFixed(4)}, 경도: {person.longitude.toFixed(4)}
                </Text>
              )}
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

export default function MapScreen() {
  const [location, setLocation] = useState(null);
  const [missingPersons, setMissingPersons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  // 초기 데이터 로드
  useEffect(() => {
    (async () => {
      try {
        // 실종자 데이터 가져오기
        const data = await api.getMissingPersons({ limit: 100 });
        setMissingPersons(data);
      } catch (error) {
        console.error('Error loading data:', error);
        setErrorMsg('데이터를 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>데이터 로딩 중...</Text>
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

  // 웹에서는 간단한 위치 리스트로 표시
  if (isWeb) {
    return (
      <View style={styles.container}>
        <View style={styles.statsOverlay}>
          <Text style={styles.statsText}>
            📍 총 {missingPersons.length}개 위치
          </Text>
        </View>
        
        {missingPersons.length > 0 ? (
          <WebMapView missingPersons={missingPersons} />
        ) : (
          <View style={styles.centered}>
            <Text style={styles.emptyText}>표시할 위치가 없습니다</Text>
            <Text style={styles.emptySubtext}>
              백엔드에서 데이터를 추가해주세요
            </Text>
          </View>
        )}
      </View>
    );
  }

  // 모바일에서는 react-native-maps 사용
  // (나중에 휴대폰에서 테스트할 때 실제 지도 표시됨)
  return (
    <View style={styles.container}>
      <View style={styles.centered}>
        <Text style={styles.infoText}>
          🗺️ 실제 지도는 모바일 앱에서 확인하세요!
        </Text>
        <Text style={styles.infoSubtext}>
          Expo Go 앱으로 QR 코드를 스캔하면{'\n'}
          Google Maps 기반 지도를 볼 수 있습니다.
        </Text>
      </View>
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
  statsOverlay: {
    backgroundColor: '#007AFF',
    padding: 15,
    alignItems: 'center',
  },
  statsText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  // 웹 지도 스타일
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
    borderLeftColor: '#FF3B30',
  },
  locationNumber: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#FF3B30',
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
  locationCoords: {
    fontSize: 12,
    color: '#999',
  },
  emptyText: {
    fontSize: 18,
    color: '#666',
    fontWeight: '600',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
  infoText: {
    fontSize: 24,
    color: '#333',
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 16,
  },
  infoSubtext: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
  },
});
