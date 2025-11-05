import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import Slider from '@react-native-community/slider';

const { width } = Dimensions.get('window');

interface DateFilterProps {
  onFilterChange: (days: number) => void;
  initialDays?: number;
}

/**
 * 미니멀 날짜 필터 컴포넌트
 * 
 * 사용법:
 * <DateFilter 
 *   onFilterChange={(days) => fetchData(days)}
 *   initialDays={30}
 * />
 */
const DateFilter: React.FC<DateFilterProps> = ({ 
  onFilterChange, 
  initialDays = 30 
}) => {
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedDays, setSelectedDays] = useState(initialDays);
  const [tempDays, setTempDays] = useState(initialDays);

  // 날짜 범위 계산
  const getDateRange = (days: number) => {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - days);

    const formatDate = (date: Date) => {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}.${month}.${day}`;
    };

    return `${formatDate(startDate)} ~ ${formatDate(endDate)}`;
  };

  // 적용 버튼
  const handleApply = () => {
    setSelectedDays(tempDays);
    onFilterChange(tempDays);
    setModalVisible(false);
  };

  // 취소 버튼
  const handleCancel = () => {
    setTempDays(selectedDays);
    setModalVisible(false);
  };

  return (
    <View>
      {/* 상단 표시줄 */}
      <TouchableOpacity 
        style={styles.filterBar}
        onPress={() => setModalVisible(true)}
      >
        <View style={styles.filterInfo}>
          <Text style={styles.filterIcon}>📅</Text>
          <View>
            <Text style={styles.filterLabel}>최근 {selectedDays}일</Text>
            <Text style={styles.filterDate}>{getDateRange(selectedDays)}</Text>
          </View>
        </View>
        <Text style={styles.changeButton}>변경</Text>
      </TouchableOpacity>

      {/* 모달 (팝업) */}
      <Modal
        animationType="slide"
        transparent={true}
        visible={modalVisible}
        onRequestClose={handleCancel}
      >
        <TouchableOpacity 
          style={styles.modalOverlay}
          activeOpacity={1}
          onPress={handleCancel}
        >
          <View style={styles.modalContent}>
            <TouchableOpacity activeOpacity={1}>
              {/* 헤더 */}
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>기간 선택</Text>
                <TouchableOpacity onPress={handleCancel}>
                  <Text style={styles.closeButton}>✕</Text>
                </TouchableOpacity>
              </View>

              {/* 슬라이더 */}
              <View style={styles.sliderContainer}>
                <Text style={styles.daysLabel}>최근 {tempDays}일</Text>
                <Text style={styles.dateRange}>{getDateRange(tempDays)}</Text>
                
                <Slider
                  style={styles.slider}
                  minimumValue={1}
                  maximumValue={365}
                  step={1}
                  value={tempDays}
                  onValueChange={setTempDays}
                  minimumTrackTintColor="#007AFF"
                  maximumTrackTintColor="#E5E5EA"
                  thumbTintColor="#007AFF"
                />

                <View style={styles.sliderLabels}>
                  <Text style={styles.sliderLabelText}>1일</Text>
                  <Text style={styles.sliderLabelText}>365일</Text>
                </View>
              </View>

              {/* 빠른 선택 버튼 */}
              <View style={styles.quickButtons}>
                {[7, 30, 90, 180, 365].map((days) => (
                  <TouchableOpacity
                    key={days}
                    style={[
                      styles.quickButton,
                      tempDays === days && styles.quickButtonActive,
                    ]}
                    onPress={() => setTempDays(days)}
                  >
                    <Text
                      style={[
                        styles.quickButtonText,
                        tempDays === days && styles.quickButtonTextActive,
                      ]}
                    >
                      {days}일
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>

              {/* 액션 버튼 */}
              <View style={styles.actionButtons}>
                <TouchableOpacity
                  style={[styles.button, styles.cancelButton]}
                  onPress={handleCancel}
                >
                  <Text style={styles.cancelButtonText}>취소</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.button, styles.applyButton]}
                  onPress={handleApply}
                >
                  <Text style={styles.applyButtonText}>적용</Text>
                </TouchableOpacity>
              </View>
            </TouchableOpacity>
          </View>
        </TouchableOpacity>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  // 상단 필터 바
  filterBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  filterInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  filterIcon: {
    fontSize: 24,
  },
  filterLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
  },
  filterDate: {
    fontSize: 12,
    color: '#8E8E93',
    marginTop: 2,
  },
  changeButton: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '500',
  },

  // 모달
  modalOverlay: {
    flex: 1,
    justifyContent: 'flex-end',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    paddingBottom: 34,
    maxHeight: '70%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#000',
  },
  closeButton: {
    fontSize: 24,
    color: '#8E8E93',
  },

  // 슬라이더
  sliderContainer: {
    padding: 24,
  },
  daysLabel: {
    fontSize: 32,
    fontWeight: '700',
    color: '#000',
    textAlign: 'center',
    marginBottom: 8,
  },
  dateRange: {
    fontSize: 14,
    color: '#8E8E93',
    textAlign: 'center',
    marginBottom: 32,
  },
  slider: {
    width: '100%',
    height: 40,
  },
  sliderLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  sliderLabelText: {
    fontSize: 12,
    color: '#8E8E93',
  },

  // 빠른 선택 버튼
  quickButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingHorizontal: 24,
    marginBottom: 24,
  },
  quickButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 16,
    backgroundColor: '#F2F2F7',
  },
  quickButtonActive: {
    backgroundColor: '#007AFF',
  },
  quickButtonText: {
    fontSize: 14,
    color: '#000',
    fontWeight: '500',
  },
  quickButtonTextActive: {
    color: '#fff',
  },

  // 액션 버튼
  actionButtons: {
    flexDirection: 'row',
    paddingHorizontal: 24,
    gap: 12,
  },
  button: {
    flex: 1,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: '#F2F2F7',
  },
  applyButton: {
    backgroundColor: '#007AFF',
  },
  cancelButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
  },
  applyButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
});

export default DateFilter;
