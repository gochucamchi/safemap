import React, { useState } from 'react';
import {
  View,
  Text,
  Modal,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Image,
  Dimensions,
  Platform,
} from 'react-native';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface DetailModalProps {
  visible: boolean;
  onClose: () => void;
  person: any;
  isAuthenticated?: boolean;
}

export default function DetailModal({ visible, onClose, person, isAuthenticated = false }: DetailModalProps) {
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);

  if (!person) return null;

  // 디버깅: person 객체 전체 출력
  console.log('DetailModal - Full person object:', JSON.stringify(person, null, 2));

  // 사진 URL 파싱 (JSON 문자열에서 배열로)
  let photos: string[] = [];
  if (person.photo_urls) {
    try {
      console.log('Raw photo_urls:', person.photo_urls);
      console.log('Type of photo_urls:', typeof person.photo_urls);
      photos = JSON.parse(person.photo_urls);
      console.log('Parsed photos:', photos);
    } catch (e) {
      console.error('Failed to parse photo_urls:', e);
      photos = [];
    }
  } else {
    console.log('No photo_urls in person data');
  }

  console.log('Final photos array:', photos);
  console.log('Photos length:', photos.length);

  // 현재 나이 계산
  const calculateCurrentAge = () => {
    if (!person.age_at_disappearance || !person.missing_date) return null;
    const missingYear = new Date(person.missing_date).getFullYear();
    const currentYear = new Date().getFullYear();
    const yearsPassed = currentYear - missingYear;
    return person.age_at_disappearance + yearsPassed;
  };

  const currentAge = calculateCurrentAge();
  const isResolved = person.status === 'resolved';
  const canViewDetails = !isResolved || isAuthenticated;

  // 실종 해제된 경우이고 로그인하지 않았으면 제한된 정보만 표시
  if (!canViewDetails) {
    return (
      <Modal
        visible={visible}
        animationType="slide"
        transparent={true}
        onRequestClose={onClose}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.header}>
              <Text style={styles.headerTitle}>상세 정보</Text>
              <TouchableOpacity onPress={onClose} style={styles.closeButton}>
                <Text style={styles.closeButtonText}>✕</Text>
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.scrollContent}>
              <View style={styles.restrictedAccess}>
                <Text style={styles.restrictedIcon}>🔒</Text>
                <Text style={styles.restrictedTitle}>로그인이 필요합니다</Text>
                <Text style={styles.restrictedText}>
                  실종 해제된 사람의 상세 정보는{'\n'}
                  개인정보 보호를 위해{'\n'}
                  로그인 후 열람 가능합니다.
                </Text>
                <View style={styles.basicInfoBox}>
                  <Text style={styles.basicInfoTitle}>기본 정보</Text>
                  <InfoRow label="발생일시" value={new Date(person.missing_date).toLocaleDateString('ko-KR')} />
                  <InfoRow label="발생장소" value={person.location_address} />
                  {person.age_at_disappearance && <InfoRow label="당시 나이" value={`${person.age_at_disappearance}세`} />}
                  {person.gender && <InfoRow label="성별" value={person.gender === 'M' ? '남성' : '여성'} />}
                </View>
              </View>
            </ScrollView>
          </View>
        </View>
      </Modal>
    );
  }

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={true}
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <View style={styles.header}>
            <Text style={styles.headerTitle}>상세 정보</Text>
            <TouchableOpacity onPress={onClose} style={styles.closeButton}>
              <Text style={styles.closeButtonText}>✕</Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.scrollContent}>
            {/* 사진 슬라이더 */}
            {photos.length > 0 ? (
              <View style={styles.photoSection}>
                <ScrollView
                  horizontal
                  pagingEnabled
                  showsHorizontalScrollIndicator={false}
                  onMomentumScrollEnd={(e) => {
                    const newIndex = Math.round(e.nativeEvent.contentOffset.x / (SCREEN_WIDTH - 80));
                    setCurrentPhotoIndex(newIndex);
                  }}
                >
                  {photos.map((photo, index) => (
                    <View key={index} style={styles.photoContainer}>
                      <Image
                        source={{ uri: photo }}
                        style={styles.photo}
                        resizeMode="contain"
                      />
                    </View>
                  ))}
                </ScrollView>
                {photos.length > 1 && (
                  <View style={styles.photoIndicator}>
                    {photos.map((_, index) => (
                      <View
                        key={index}
                        style={[
                          styles.indicatorDot,
                          index === currentPhotoIndex && styles.indicatorDotActive,
                        ]}
                      />
                    ))}
                  </View>
                )}
              </View>
            ) : (
              <View style={styles.photoSection}>
                <View style={styles.noPhotoContainer}>
                  <Text style={styles.noPhotoIcon}>📷</Text>
                  <Text style={styles.noPhotoText}>사진 없음</Text>
                  <Text style={styles.noPhotoDebug}>
                    디버그: photo_urls = {person.photo_urls ? `"${person.photo_urls}"` : 'null'}
                  </Text>
                </View>
              </View>
            )}

            {/* 상태 배지 */}
            <View style={styles.statusBadgeContainer}>
              <View style={[styles.statusBadge, isResolved ? styles.resolvedBadge : styles.missingBadge]}>
                <Text style={styles.statusBadgeText}>
                  {isResolved ? '실종 해제' : '실종 중'}
                </Text>
              </View>
            </View>

            {/* 기본 정보 */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>기본 정보</Text>
              {person.name && <InfoRow label="이름" value={person.name} />}
              {person.age_at_disappearance && (
                <InfoRow
                  label="나이"
                  value={`당시 ${person.age_at_disappearance}세${currentAge ? ` / 현재 약 ${currentAge}세` : ''}`}
                />
              )}
              {person.gender && <InfoRow label="성별" value={person.gender === 'M' ? '남성' : '여성'} />}
              {person.nationality && <InfoRow label="국적" value={person.nationality} />}
            </View>

            {/* 발생 정보 */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>발생 정보</Text>
              <InfoRow label="발생일시" value={new Date(person.missing_date).toLocaleString('ko-KR')} />
              <InfoRow label="발생장소" value={person.location_address} />
              {person.location_detail && <InfoRow label="장소 상세" value={person.location_detail} />}
            </View>

            {/* 신체 특징 */}
            {(person.height || person.weight || person.body_type || person.face_shape || person.hair_color || person.hair_style) && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>신체 특징</Text>
                {person.height && <InfoRow label="키" value={`${person.height}cm`} />}
                {person.weight && <InfoRow label="몸무게" value={`${person.weight}kg`} />}
                {person.body_type && <InfoRow label="체격" value={person.body_type} />}
                {person.face_shape && <InfoRow label="얼굴형" value={person.face_shape} />}
                {person.hair_color && <InfoRow label="두발색상" value={person.hair_color} />}
                {person.hair_style && <InfoRow label="두발형태" value={person.hair_style} />}
              </View>
            )}

            {/* 착의사항 */}
            {person.clothing_description && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>착의사항</Text>
                <Text style={styles.descriptionText}>{person.clothing_description}</Text>
              </View>
            )}

            {/* 기타 특징 */}
            {person.special_features && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>기타 특이사항</Text>
                <Text style={styles.descriptionText}>{person.special_features}</Text>
              </View>
            )}

            {/* 실종 해제 정보 */}
            {isResolved && person.resolved_at && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>실종 해제</Text>
                <InfoRow label="해제일시" value={new Date(person.resolved_at).toLocaleString('ko-KR')} />
              </View>
            )}
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
}

// 정보 행 컴포넌트
const InfoRow = ({ label, value }: { label: string; value: string }) => (
  <View style={styles.infoRow}>
    <Text style={styles.infoLabel}>{label}</Text>
    <Text style={styles.infoValue}>{value}</Text>
  </View>
);

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '90%',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#000',
  },
  closeButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#F2F2F7',
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeButtonText: {
    fontSize: 20,
    color: '#666',
  },
  scrollContent: {
    padding: 20,
  },
  photoSection: {
    marginBottom: 20,
  },
  photoContainer: {
    width: SCREEN_WIDTH - 80,
    height: 300,
    backgroundColor: '#F2F2F7',
    borderRadius: 12,
    marginRight: 10,
    overflow: 'hidden',
    justifyContent: 'center',
    alignItems: 'center',
  },
  photo: {
    width: '100%',
    height: '100%',
  },
  photoIndicator: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 10,
    gap: 6,
  },
  indicatorDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#D1D1D6',
  },
  indicatorDotActive: {
    backgroundColor: '#007AFF',
  },
  statusBadgeContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  statusBadge: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 16,
  },
  missingBadge: {
    backgroundColor: '#FF3B30',
  },
  resolvedBadge: {
    backgroundColor: '#34C759',
  },
  statusBadgeText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 12,
  },
  infoRow: {
    flexDirection: 'row',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  },
  infoLabel: {
    fontSize: 15,
    color: '#666',
    width: 100,
    fontWeight: '500',
  },
  infoValue: {
    flex: 1,
    fontSize: 15,
    color: '#000',
  },
  descriptionText: {
    fontSize: 15,
    color: '#333',
    lineHeight: 22,
  },
  restrictedAccess: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  restrictedIcon: {
    fontSize: 60,
    marginBottom: 16,
  },
  restrictedTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 8,
  },
  restrictedText: {
    fontSize: 15,
    color: '#666',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 24,
  },
  basicInfoBox: {
    width: '100%',
    backgroundColor: '#F2F2F7',
    borderRadius: 12,
    padding: 16,
  },
  basicInfoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
    marginBottom: 12,
  },
  noPhotoContainer: {
    height: 200,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F2F2F7',
    borderRadius: 12,
  },
  noPhotoIcon: {
    fontSize: 48,
    marginBottom: 8,
  },
  noPhotoText: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
  },
  noPhotoDebug: {
    fontSize: 12,
    color: '#999',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
});
