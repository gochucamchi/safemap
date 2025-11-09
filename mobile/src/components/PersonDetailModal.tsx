import React, { useState } from 'react';
import {
  Modal,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Image,
  Dimensions,
} from 'react-native';
import { API_BASE_URL } from '../services/api';

interface PersonDetailModalProps {
  visible: boolean;
  person: any;
  onClose: () => void;
}

const { width: SCREEN_WIDTH } = Dimensions.get('window');
const PHOTO_WIDTH = SCREEN_WIDTH - 32; // 양쪽 패딩 16씩
const PHOTO_HEIGHT = 300;

export default function PersonDetailModal({ visible, person, onClose }: PersonDetailModalProps) {
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);

  if (!person) return null;

  const photoUrls = person.photo_urls || [];
  const hasPhotos = photoUrls.length > 0;

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={true}
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          {/* 헤더 */}
          <View style={styles.header}>
            <Text style={styles.headerTitle}>실종자 상세정보</Text>
            <TouchableOpacity onPress={onClose} style={styles.closeButton}>
              <Text style={styles.closeButtonText}>✕</Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
            {/* 사진 영역 */}
            {hasPhotos ? (
              <View style={styles.photoContainer}>
                <Image
                  source={{ uri: `${API_BASE_URL}${photoUrls[currentPhotoIndex]}` }}
                  style={styles.photo}
                  resizeMode="contain"
                />
                {photoUrls.length > 1 && (
                  <View style={styles.photoNavigation}>
                    <TouchableOpacity
                      style={[styles.navButton, currentPhotoIndex === 0 && styles.navButtonDisabled]}
                      onPress={() => setCurrentPhotoIndex(Math.max(0, currentPhotoIndex - 1))}
                      disabled={currentPhotoIndex === 0}
                    >
                      <Text style={styles.navButtonText}>‹</Text>
                    </TouchableOpacity>
                    <Text style={styles.photoCounter}>
                      {currentPhotoIndex + 1} / {photoUrls.length}
                    </Text>
                    <TouchableOpacity
                      style={[styles.navButton, currentPhotoIndex === photoUrls.length - 1 && styles.navButtonDisabled]}
                      onPress={() => setCurrentPhotoIndex(Math.min(photoUrls.length - 1, currentPhotoIndex + 1))}
                      disabled={currentPhotoIndex === photoUrls.length - 1}
                    >
                      <Text style={styles.navButtonText}>›</Text>
                    </TouchableOpacity>
                  </View>
                )}
              </View>
            ) : (
              <View style={styles.noPhotoContainer}>
                <Text style={styles.noPhotoText}>📷</Text>
                <Text style={styles.noPhotoSubtext}>등록된 사진이 없습니다</Text>
              </View>
            )}

            {/* 기본 정보 */}
            <View style={styles.infoSection}>
              <Text style={styles.sectionTitle}>📋 기본 정보</Text>

              {person.age && person.gender && (
                <View style={styles.infoRow}>
                  <Text style={styles.infoLabel}>성별 / 나이</Text>
                  <Text style={styles.infoValue}>
                    {person.gender === 'M' ? '남성' : '여성'} · {person.age}세
                  </Text>
                </View>
              )}

              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>실종일</Text>
                <Text style={styles.infoValue}>
                  {new Date(person.missing_date).toLocaleDateString('ko-KR', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </Text>
              </View>

              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>상태</Text>
                <View style={[styles.statusBadge, person.status === 'missing' ? styles.missingBadge : styles.resolvedBadge]}>
                  <Text style={styles.statusBadgeText}>
                    {person.status === 'missing' ? '🔴 실종 중' : '🟢 실종 해제'}
                  </Text>
                </View>
              </View>

              {person.status === 'resolved' && person.resolved_at && (
                <View style={styles.infoRow}>
                  <Text style={styles.infoLabel}>해제일</Text>
                  <Text style={styles.infoValue}>
                    {new Date(person.resolved_at).toLocaleDateString('ko-KR', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </Text>
                </View>
              )}
            </View>

            {/* 신체특징 / 착의사항 */}
            {person.location_detail && (
              <View style={styles.infoSection}>
                <Text style={styles.sectionTitle}>👤 신체특징 / 착의사항</Text>
                <Text style={styles.detailText}>{person.location_detail}</Text>
              </View>
            )}

            {/* 실종 위치 */}
            <View style={styles.infoSection}>
              <Text style={styles.sectionTitle}>📍 실종 위치</Text>

              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>주소</Text>
                <Text style={styles.infoValue}>{person.location_address || 'N/A'}</Text>
              </View>
            </View>
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
}

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
    paddingBottom: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#333',
  },
  closeButton: {
    padding: 4,
  },
  closeButtonText: {
    fontSize: 24,
    color: '#666',
    fontWeight: '300',
  },
  scrollView: {
    paddingHorizontal: 16,
  },

  // 사진
  photoContainer: {
    marginTop: 16,
    marginBottom: 20,
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    overflow: 'hidden',
  },
  photo: {
    width: PHOTO_WIDTH,
    height: PHOTO_HEIGHT,
    backgroundColor: '#E5E5EA',
  },
  photoNavigation: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: '#fff',
  },
  navButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  navButtonDisabled: {
    backgroundColor: '#E5E5EA',
  },
  navButtonText: {
    fontSize: 24,
    color: '#fff',
    fontWeight: '600',
  },
  photoCounter: {
    fontSize: 14,
    color: '#666',
    fontWeight: '600',
  },
  noPhotoContainer: {
    height: PHOTO_HEIGHT,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    marginTop: 16,
    marginBottom: 20,
  },
  noPhotoText: {
    fontSize: 48,
    marginBottom: 8,
  },
  noPhotoSubtext: {
    fontSize: 14,
    color: '#999',
  },

  // 정보 섹션
  infoSection: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#333',
    marginBottom: 12,
  },
  detailText: {
    fontSize: 14,
    color: '#333',
    lineHeight: 22,
    backgroundColor: '#F9F9F9',
    padding: 12,
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#007AFF',
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#F5F5F5',
  },
  infoLabel: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
    flex: 1,
  },
  infoValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: '600',
    flex: 2,
    textAlign: 'right',
  },
  infoValueMultiline: {
    fontSize: 14,
    color: '#333',
    fontWeight: '600',
    flex: 2,
    textAlign: 'right',
    lineHeight: 20,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  missingBadge: {
    backgroundColor: '#FF3B30',
  },
  resolvedBadge: {
    backgroundColor: '#34C759',
  },
  statusBadgeText: {
    color: '#fff',
    fontSize: 13,
    fontWeight: '700',
  },
});
