import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { api } from '../services/api';

export default function StatsScreen() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // 데이터 로드
  const loadData = async () => {
    try {
      const data = await api.getStatistics(30);
      setStats(data);
    } catch (error) {
      console.error('Error loading statistics:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // 새로고침 핸들러
  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  if (!stats) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>통계 데이터를 불러올 수 없습니다</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* 전체 통계 카드 */}
      <View style={styles.mainCard}>
        <Text style={styles.mainCardTitle}>최근 {stats.period_days}일</Text>
        <Text style={styles.mainCardNumber}>{stats.total_count}</Text>
        <Text style={styles.mainCardSubtitle}>총 실종 사건</Text>
      </View>

      {/* 성별 통계 */}
      <View style={styles.sectionCard}>
        <Text style={styles.sectionTitle}>성별 통계</Text>
        <View style={styles.statsRow}>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>남성</Text>
            <Text style={[styles.statNumber, { color: '#007AFF' }]}>
              {stats.gender_statistics?.M || 0}
            </Text>
            <Text style={styles.statPercent}>
              {stats.total_count > 0
                ? `${Math.round((stats.gender_statistics?.M || 0) / stats.total_count * 100)}%`
                : '0%'}
            </Text>
          </View>
          <View style={styles.divider} />
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>여성</Text>
            <Text style={[styles.statNumber, { color: '#FF3B30' }]}>
              {stats.gender_statistics?.F || 0}
            </Text>
            <Text style={styles.statPercent}>
              {stats.total_count > 0
                ? `${Math.round((stats.gender_statistics?.F || 0) / stats.total_count * 100)}%`
                : '0%'}
            </Text>
          </View>
        </View>
      </View>

      {/* 지역별 통계 */}
      <View style={styles.sectionCard}>
        <Text style={styles.sectionTitle}>상위 발생 지역</Text>
        {stats.top_locations && stats.top_locations.length > 0 ? (
          stats.top_locations.map((location, index) => (
            <View key={index} style={styles.locationItem}>
              <View style={styles.locationRank}>
                <Text style={styles.locationRankText}>{index + 1}</Text>
              </View>
              <Text style={styles.locationName} numberOfLines={1}>
                {location.region}
              </Text>
              <Text style={styles.locationCount}>{location.count}건</Text>
            </View>
          ))
        ) : (
          <Text style={styles.emptyText}>데이터가 없습니다</Text>
        )}
      </View>

      {/* 안전 정보 */}
      <View style={styles.infoCard}>
        <Text style={styles.infoTitle}>💡 안전 수칙</Text>
        <Text style={styles.infoText}>
          • 외출 시 가족에게 행선지를 알리세요{'\n'}
          • 늦은 시간 인적이 드문 곳은 피하세요{'\n'}
          • 긴급 상황 시 112로 신고하세요{'\n'}
          • 실종 아동 발견 시 182로 신고하세요
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  content: {
    padding: 15,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    fontSize: 16,
    color: '#666',
  },
  mainCard: {
    backgroundColor: '#007AFF',
    borderRadius: 16,
    padding: 30,
    alignItems: 'center',
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  mainCardTitle: {
    fontSize: 16,
    color: '#fff',
    opacity: 0.9,
    marginBottom: 10,
  },
  mainCardNumber: {
    fontSize: 56,
    fontWeight: 'bold',
    color: '#fff',
  },
  mainCardSubtitle: {
    fontSize: 18,
    color: '#fff',
    opacity: 0.9,
    marginTop: 5,
  },
  sectionCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  divider: {
    width: 1,
    backgroundColor: '#E0E0E0',
    marginHorizontal: 10,
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  statNumber: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  statPercent: {
    fontSize: 14,
    color: '#999',
    marginTop: 4,
  },
  locationItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  locationRank: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  locationRankText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 14,
  },
  locationName: {
    flex: 1,
    fontSize: 16,
    color: '#333',
  },
  locationCount: {
    fontSize: 16,
    fontWeight: '600',
    color: '#007AFF',
  },
  emptyText: {
    textAlign: 'center',
    color: '#999',
    fontSize: 14,
    paddingVertical: 20,
  },
  infoCard: {
    backgroundColor: '#FFF9E6',
    borderRadius: 12,
    padding: 20,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#FFE699',
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  infoText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 24,
  },
});
