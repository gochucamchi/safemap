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

export default function ListScreen() {
  const [missingPersons, setMissingPersons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedDays, setSelectedDays] = useState(30);

  // 데이터 로드 (날짜 필터 적용)
  const loadData = async (days = 30) => {
    try {
      const data = await api.getMissingPersons({ 
        limit: 100,
        days: days
      });
      
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

  // selectedDays가 변경되면 데이터 다시 로드
  useEffect(() => {
    loadData(selectedDays);
  }, [selectedDays]);

  // 날짜 필터 변경 핸들러
  const handleFilterChange = (days) => {
    setSelectedDays(days);
  };

  // 새로고침 핸들러
  const onRefresh = () => {
    setRefreshing(true);
    loadData(selectedDays);
  };

  // 리스트 아이템 렌더링
  const renderItem = ({ item }) => (
    <TouchableOpacity style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.date}>
          {new Date(item.missing_date).toLocaleDateString('ko-KR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          })}
        </Text>
        <View style={[styles.badge, styles.missingBadge]}>
          <Text style={styles.badgeText}>실종</Text>
        </View>
      </View>
      
      <View style={styles.cardBody}>
        <Text style={styles.location} numberOfLines={2}>
          📍 {item.location_address}
        </Text>
        
        {item.age && item.gender && (
          <Text style={styles.info}>
            {item.gender === 'M' ? '남성' : '여성'} · {item.age}세
          </Text>
        )}
        
        {item.location_detail && (
          <Text style={styles.detail} numberOfLines={2}>
            {item.location_detail}
          </Text>
        )}
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* DateFilter 추가 */}
      <DateFilter 
        onFilterChange={handleFilterChange}
        initialDays={30}
      />

      {/* 결과 개수 표시 */}
      {missingPersons.length > 0 && (
        <View style={styles.resultBar}>
          <Text style={styles.resultText}>
            총 {missingPersons.length}건의 실종 사건
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
