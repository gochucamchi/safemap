import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  StyleSheet,
  ActivityIndicator,
  Text,
  TouchableOpacity,
  Platform,
} from 'react-native';
import { api } from '../services/api';
import AdvancedFilterModal from '../components/AdvancedFilterModal';

// Platform별 WebView import
let WebView: any = null;
if (Platform.OS !== 'web') {
  try {
    WebView = require('react-native-webview').WebView;
  } catch (e) {
    console.log('WebView not available');
  }
}

// 웹 전용 지도 컴포넌트 (iframe 사용)
const WebMapComponent = ({ html }: { html: string }) => {
  if (Platform.OS !== 'web') return null;

  // @ts-ignore - iframe은 웹에서만 사용
  return React.createElement('iframe', {
    srcDoc: html,
    style: {
      flex: 1,
      width: '100%',
      height: '100%',
      border: 'none',
    },
    title: 'Kakao Map',
  });
};

// Kakao Maps HTML 템플릿
const getKakaoMapHTML = (markers: any[], dangerZones: any[]) => {
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <style>
    * { margin: 0; padding: 0; }
    html, body, #map { width: 100%; height: 100%; }
    .custom-overlay {
      position: relative;
      bottom: 85px;
      border-radius: 8px;
      border: 1px solid #ccc;
      background: white;
      padding: 8px 12px;
      font-size: 13px;
      font-family: -apple-system, sans-serif;
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }
    .custom-overlay .title {
      font-weight: 600;
      margin-bottom: 4px;
      color: #333;
    }
    .custom-overlay .info {
      font-size: 11px;
      color: #666;
    }
    .custom-overlay:after {
      content: '';
      position: absolute;
      bottom: -12px;
      left: 50%;
      width: 0;
      height: 0;
      border: 6px solid transparent;
      border-top-color: white;
      border-bottom: 0;
      margin-left: -6px;
    }
    .legend {
      position: absolute;
      top: 10px;
      right: 10px;
      background: white;
      padding: 10px;
      border-radius: 8px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
      font-size: 12px;
      z-index: 1000;
    }
    .legend-title {
      font-weight: 600;
      margin-bottom: 8px;
      color: #333;
    }
    .legend-item {
      display: flex;
      align-items: center;
      margin-bottom: 4px;
    }
    .legend-color {
      width: 20px;
      height: 20px;
      border-radius: 4px;
      margin-right: 6px;
    }
  </style>
  <script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey=ab5b40a00e8f67e5d459b80cd7d36466&libraries=clusterer"></script>
</head>
<body>
  <div id="map"></div>
  <div class="legend">
    <div class="legend-title">🗺️ 범례</div>
    <div class="legend-item">
      <div class="legend-color" style="background: rgba(255, 0, 0, 0.4); border: 2px solid #FF0000;"></div>
      <span>고위험 지역</span>
    </div>
    
    <div class="legend-item">
      <div class="legend-color" style="background: rgba(255, 165, 0, 0.4); border: 2px solid #FFA500;"></div>
      <span>중위험 지역</span>
    </div>
    <div class="legend-item">
      <div class="legend-color" style="background: rgba(255, 255, 0, 0.4); border: 2px solid #FFFF00;"></div>
      <span>저위험 지역</span>
    </div>
    <div class="legend-item">
      <div class="legend-color" style="background: #FF3B30; border-radius: 50%;"></div>
      <span>실종 중</span>
    </div>
    <div class="legend-item">
      <div class="legend-color" style="background: #34C759; border-radius: 50%;"></div>
      <span>실종 해제</span>
    </div>
  </div>
  <script>
    // Kakao Maps API Key가 없으면 경고 표시
    if (typeof kakao === 'undefined') {
      document.body.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;text-align:center;padding:20px;"><div><h2>⚠️ Kakao Maps API 키 필요</h2><p style="margin-top:10px;color:#666;">Kakao Developers에서 앱 키를 발급받아 YOUR_APP_KEY를 교체하세요</p></div></div>';
    } else {
      var markers = ${JSON.stringify(markers)};
      var dangerZones = ${JSON.stringify(dangerZones)};

      // 지도 중심 계산
      var centerLat = markers.length > 0
        ? markers.reduce((sum, m) => sum + m.lat, 0) / markers.length
        : 37.5665;
      var centerLng = markers.length > 0
        ? markers.reduce((sum, m) => sum + m.lng, 0) / markers.length
        : 126.9780;

      var mapContainer = document.getElementById('map');
      var mapOption = {
        center: new kakao.maps.LatLng(centerLat, centerLng),
        level: 7
      };

      var map = new kakao.maps.Map(mapContainer, mapOption);

      // 위험 지역 표시 (원형)
      dangerZones.forEach(function(zone) {
        var circle = new kakao.maps.Circle({
          center: new kakao.maps.LatLng(zone.lat, zone.lng),
          radius: zone.radius,
          strokeWeight: 2,
          strokeColor: zone.color,
          strokeOpacity: 0.8,
          strokeStyle: 'solid',
          fillColor: zone.color,
          fillOpacity: 0.3
        });
        circle.setMap(map);
      });

      // 마커 표시
      markers.forEach(function(markerData) {
        var markerPosition = new kakao.maps.LatLng(markerData.lat, markerData.lng);

        // 마커 이미지 생성
        var imageSrc = markerData.status === 'missing'
          ? 'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/markerStar.png'
          : 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMzUiIHZpZXdCb3g9IjAgMCAyNCAzNSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIgMEMxOC42MjcgMCAyNCA1LjM3MyAyNCAxMkMyNCAyMS43NSAxMiAzNSAxMiAzNUMxMiAzNSAwIDIxLjc1IDAgMTJDMCA1LjM3MyA1LjM3MyAwIDEyIDBaIiBmaWxsPSIjMzRDNzU5Ii8+PC9zdmc+';

        var imageSize = new kakao.maps.Size(24, 35);
        var markerImage = new kakao.maps.MarkerImage(imageSrc, imageSize);

        var marker = new kakao.maps.Marker({
          position: markerPosition,
          image: markerImage
        });

        marker.setMap(map);

        // 커스텀 오버레이
        var content = '<div class="custom-overlay">' +
          '<div class="title">' + (markerData.status === 'missing' ? '🔴 실종 중' : '🟢 실종 해제') + '</div>' +
          '<div class="info">' + markerData.address + '</div>' +
          '<div class="info">' + markerData.date + '</div>' +
          (markerData.personInfo ? '<div class="info">' + markerData.personInfo + '</div>' : '') +
          '</div>';

        var customOverlay = new kakao.maps.CustomOverlay({
          position: markerPosition,
          content: content,
          yAnchor: 1
        });

        // 마커 클릭 이벤트
        kakao.maps.event.addListener(marker, 'click', function() {
          customOverlay.setMap(map);
        });

        // 지도 클릭 시 오버레이 닫기
        kakao.maps.event.addListener(map, 'click', function() {
          customOverlay.setMap(null);
        });
      });
    }
  </script>
</body>
</html>
  `;
};

export default function MapScreen() {
  const [missingPersons, setMissingPersons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [activeTab, setActiveTab] = useState<'all' | 'missing' | 'resolved'>('all');
  const [showAdvancedFilter, setShowAdvancedFilter] = useState(false);
  const [advancedFilters, setAdvancedFilters] = useState<any>({});
  const webViewRef = useRef(null);

  // 위험도 계산 함수
  const calculateDangerZones = (persons: any[]) => {
    // 위치가 있는 실종 중인 사람들만 필터
    const missingWithLocation = persons.filter(
      (p) => p.status === 'missing' && p.latitude && p.longitude
    );

    if (missingWithLocation.length === 0) return [];

    // 지역별로 그룹화 (0.05도 단위 ≈ 약 5km)
    const gridSize = 0.05;
    const grid: { [key: string]: any[] } = {};

    missingWithLocation.forEach((person) => {
      const gridLat = Math.floor(person.latitude / gridSize) * gridSize;
      const gridLng = Math.floor(person.longitude / gridSize) * gridSize;
      const key = `${gridLat},${gridLng}`;

      if (!grid[key]) {
        grid[key] = [];
      }
      grid[key].push(person);
    });

    // 위험도 계산
    const dangerZones = Object.entries(grid)
      .filter(([_, persons]) => persons.length >= 2) // 2건 이상인 지역만
      .map(([key, persons]) => {
        const [lat, lng] = key.split(',').map(Number);
        const count = persons.length;

        // 위험도 레벨 결정
        let color = '#FFFF00'; // 노랑 (저위험)
        let radius = 3000; // 3km

        if (count >= 5) {
          color = '#FF0000'; // 빨강 (고위험)
          radius = 5000; // 5km
        } else if (count >= 3) {
          color = '#FFA500'; // 주황 (중위험)
          radius = 4000; // 4km
        }

        // 실제 중심 계산
        const centerLat = persons.reduce((sum, p) => sum + p.latitude, 0) / count;
        const centerLng = persons.reduce((sum, p) => sum + p.longitude, 0) / count;

        return {
          lat: centerLat,
          lng: centerLng,
          radius,
          color,
          count,
        };
      });

    return dangerZones;
  };

  // 데이터 로드 함수
  const loadData = async (status = 'all', filters = {}) => {
    try {
      setLoading(true);
      const params: any = {
        limit: 500,
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

  // 마커 데이터 준비
  const markers = missingPersons
    .filter((p) => p.latitude && p.longitude)
    .map((p) => ({
      lat: p.latitude,
      lng: p.longitude,
      status: p.status,
      address: p.location_address,
      date: new Date(p.missing_date).toLocaleDateString('ko-KR'),
      personInfo: p.age && p.gender ? `${p.gender === 'M' ? '남성' : '여성'} · ${p.age}세` : null,
    }));

  // 위험 지역 계산
  const dangerZones = calculateDangerZones(missingPersons);

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
          📍 전체 {missingPersons.length}건 · 지도 표시 {withLocationCount}건
        </Text>
        <View style={styles.statsRow}>
          <Text style={styles.statsMissing}>🔴 실종 중: {missingCount}</Text>
          <Text style={styles.statsResolved}>🟢 해제: {resolvedCount}</Text>
          <Text style={styles.statsDanger}>⚠️ 위험 지역: {dangerZones.length}</Text>
        </View>
      </View>

      {/* Kakao Map */}
      {missingPersons.length > 0 ? (
        Platform.OS === 'web' ? (
          // 웹에서는 HTML을 직접 렌더링
          <WebMapComponent html={getKakaoMapHTML(markers, dangerZones)} />
        ) : WebView ? (
          // 모바일에서는 WebView 사용
          <WebView
            ref={webViewRef}
            source={{ html: getKakaoMapHTML(markers, dangerZones) }}
            style={styles.webView}
            javaScriptEnabled={true}
            domStorageEnabled={true}
            startInLoadingState={true}
            renderLoading={() => (
              <View style={styles.centered}>
                <ActivityIndicator size="large" color="#007AFF" />
              </View>
            )}
          />
        ) : (
          // WebView가 설치되지 않은 경우
          <View style={styles.centered}>
            <Text style={styles.errorText}>📦 WebView 패키지 필요</Text>
            <Text style={styles.emptySubtext}>
              npx expo install react-native-webview
            </Text>
          </View>
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
    fontSize: 15,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 4,
  },
  statsRow: {
    flexDirection: 'row',
    gap: 12,
  },
  statsMissing: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FFCCCB',
  },
  statsResolved: {
    fontSize: 12,
    fontWeight: '600',
    color: '#C8E6C9',
  },
  statsDanger: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FFE082',
  },

  // WebView
  webView: {
    flex: 1,
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
});
