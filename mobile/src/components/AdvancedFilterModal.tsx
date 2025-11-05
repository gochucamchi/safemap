import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  TouchableOpacity,
  ScrollView,
  Platform,
} from 'react-native';

interface FilterOptions {
  startDate?: string;
  endDate?: string;
  gender?: 'M' | 'F' | null;
  ageMin?: number;
  ageMax?: number;
}

interface AdvancedFilterModalProps {
  visible: boolean;
  onClose: () => void;
  onApply: (filters: FilterOptions) => void;
  initialFilters?: FilterOptions;
}

/**
 * 고급 필터 모달
 * - 날짜 직접 선택 (YYYY-MM-DD)
 * - 성별 필터 (남성/여성)
 * - 나이 범위 필터
 */
const AdvancedFilterModal: React.FC<AdvancedFilterModalProps> = ({
  visible,
  onClose,
  onApply,
  initialFilters = {},
}) => {
  const [startDate, setStartDate] = useState(initialFilters.startDate || '');
  const [endDate, setEndDate] = useState(initialFilters.endDate || '');
  const [gender, setGender] = useState<'M' | 'F' | null>(initialFilters.gender || null);
  const [ageMin, setAgeMin] = useState<number | undefined>(initialFilters.ageMin);
  const [ageMax, setAgeMax] = useState<number | undefined>(initialFilters.ageMax);

  // 날짜 선택 (간단한 버전 - 년/월/일 선택)
  const [showDatePicker, setShowDatePicker] = useState<'start' | 'end' | null>(null);
  const [tempYear, setTempYear] = useState(new Date().getFullYear());
  const [tempMonth, setTempMonth] = useState(new Date().getMonth() + 1);
  const [tempDay, setTempDay] = useState(new Date().getDate());

  const handleDateSelect = () => {
    const dateStr = `${tempYear}-${String(tempMonth).padStart(2, '0')}-${String(tempDay).padStart(2, '0')}`;
    if (showDatePicker === 'start') {
      setStartDate(dateStr);
    } else if (showDatePicker === 'end') {
      setEndDate(dateStr);
    }
    setShowDatePicker(null);
  };

  const openDatePicker = (type: 'start' | 'end') => {
    const date = type === 'start' ? startDate : endDate;
    if (date) {
      const [y, m, d] = date.split('-').map(Number);
      setTempYear(y);
      setTempMonth(m);
      setTempDay(d);
    } else {
      const now = new Date();
      setTempYear(now.getFullYear());
      setTempMonth(now.getMonth() + 1);
      setTempDay(now.getDate());
    }
    setShowDatePicker(type);
  };

  const handleApply = () => {
    onApply({
      startDate: startDate || undefined,
      endDate: endDate || undefined,
      gender: gender || undefined,
      ageMin: ageMin,
      ageMax: ageMax,
    });
    onClose();
  };

  const handleReset = () => {
    setStartDate('');
    setEndDate('');
    setGender(null);
    setAgeMin(undefined);
    setAgeMax(undefined);
  };

  const years = Array.from({ length: 10 }, (_, i) => new Date().getFullYear() - i);
  const months = Array.from({ length: 12 }, (_, i) => i + 1);
  const days = Array.from({ length: 31 }, (_, i) => i + 1);
  const ages = Array.from({ length: 101 }, (_, i) => i);

  return (
    <Modal
      animationType="slide"
      transparent={true}
      visible={visible}
      onRequestClose={onClose}
    >
      <TouchableOpacity
        style={styles.modalOverlay}
        activeOpacity={1}
        onPress={onClose}
      >
        <View style={styles.modalContent}>
          <TouchableOpacity activeOpacity={1}>
            {/* 헤더 */}
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>고급 필터</Text>
              <TouchableOpacity onPress={onClose}>
                <Text style={styles.closeButton}>✕</Text>
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.scrollContent} showsVerticalScrollIndicator={false}>
              {/* 날짜 범위 선택 */}
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>📅 날짜 범위</Text>

                <View style={styles.dateRow}>
                  <Text style={styles.dateLabel}>시작일</Text>
                  <TouchableOpacity
                    style={styles.dateButton}
                    onPress={() => openDatePicker('start')}
                  >
                    <Text style={styles.dateButtonText}>
                      {startDate || '선택 안 함'}
                    </Text>
                  </TouchableOpacity>
                </View>

                <View style={styles.dateRow}>
                  <Text style={styles.dateLabel}>종료일</Text>
                  <TouchableOpacity
                    style={styles.dateButton}
                    onPress={() => openDatePicker('end')}
                  >
                    <Text style={styles.dateButtonText}>
                      {endDate || '선택 안 함'}
                    </Text>
                  </TouchableOpacity>
                </View>
              </View>

              {/* 성별 필터 */}
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>👤 성별</Text>
                <View style={styles.genderRow}>
                  <TouchableOpacity
                    style={[styles.genderButton, gender === 'M' && styles.genderButtonActive]}
                    onPress={() => setGender(gender === 'M' ? null : 'M')}
                  >
                    <Text style={[styles.genderButtonText, gender === 'M' && styles.genderButtonTextActive]}>
                      남성
                    </Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[styles.genderButton, gender === 'F' && styles.genderButtonActive]}
                    onPress={() => setGender(gender === 'F' ? null : 'F')}
                  >
                    <Text style={[styles.genderButtonText, gender === 'F' && styles.genderButtonTextActive]}>
                      여성
                    </Text>
                  </TouchableOpacity>
                </View>
              </View>

              {/* 나이 범위 */}
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>🎂 나이 범위</Text>

                <View style={styles.ageRow}>
                  <View style={styles.ageInputContainer}>
                    <Text style={styles.ageLabel}>최소</Text>
                    <TouchableOpacity
                      style={styles.ageButton}
                      onPress={() => {
                        // 간단한 스크롤 선택기를 보여줄 수 있습니다
                        // 여기서는 단순화를 위해 버튼으로 증감
                      }}
                    >
                      <Text style={styles.ageButtonText}>
                        {ageMin !== undefined ? `${ageMin}세` : '없음'}
                      </Text>
                    </TouchableOpacity>
                    <View style={styles.ageControls}>
                      <TouchableOpacity
                        style={styles.ageControlButton}
                        onPress={() => setAgeMin((ageMin || 0) > 0 ? (ageMin || 0) - 1 : 0)}
                      >
                        <Text style={styles.ageControlText}>−</Text>
                      </TouchableOpacity>
                      <TouchableOpacity
                        style={styles.ageControlButton}
                        onPress={() => setAgeMin((ageMin || 0) + 1)}
                      >
                        <Text style={styles.ageControlText}>+</Text>
                      </TouchableOpacity>
                      <TouchableOpacity
                        style={styles.ageResetButton}
                        onPress={() => setAgeMin(undefined)}
                      >
                        <Text style={styles.ageResetText}>✕</Text>
                      </TouchableOpacity>
                    </View>
                  </View>

                  <Text style={styles.ageSeparator}>~</Text>

                  <View style={styles.ageInputContainer}>
                    <Text style={styles.ageLabel}>최대</Text>
                    <TouchableOpacity
                      style={styles.ageButton}
                    >
                      <Text style={styles.ageButtonText}>
                        {ageMax !== undefined ? `${ageMax}세` : '없음'}
                      </Text>
                    </TouchableOpacity>
                    <View style={styles.ageControls}>
                      <TouchableOpacity
                        style={styles.ageControlButton}
                        onPress={() => setAgeMax((ageMax || 1) > 0 ? (ageMax || 1) - 1 : 0)}
                      >
                        <Text style={styles.ageControlText}>−</Text>
                      </TouchableOpacity>
                      <TouchableOpacity
                        style={styles.ageControlButton}
                        onPress={() => setAgeMax((ageMax || 0) + 1)}
                      >
                        <Text style={styles.ageControlText}>+</Text>
                      </TouchableOpacity>
                      <TouchableOpacity
                        style={styles.ageResetButton}
                        onPress={() => setAgeMax(undefined)}
                      >
                        <Text style={styles.ageResetText}>✕</Text>
                      </TouchableOpacity>
                    </View>
                  </View>
                </View>
              </View>
            </ScrollView>

            {/* 액션 버튼 */}
            <View style={styles.actionButtons}>
              <TouchableOpacity
                style={[styles.button, styles.resetButton]}
                onPress={handleReset}
              >
                <Text style={styles.resetButtonText}>초기화</Text>
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

      {/* 날짜 선택 모달 */}
      {showDatePicker && (
        <Modal
          animationType="fade"
          transparent={true}
          visible={true}
          onRequestClose={() => setShowDatePicker(null)}
        >
          <TouchableOpacity
            style={styles.datePickerOverlay}
            activeOpacity={1}
            onPress={() => setShowDatePicker(null)}
          >
            <View style={styles.datePickerContent}>
              <Text style={styles.datePickerTitle}>
                {showDatePicker === 'start' ? '시작일 선택' : '종료일 선택'}
              </Text>

              <View style={styles.datePickerRow}>
                <ScrollView style={styles.datePickerColumn} showsVerticalScrollIndicator={false}>
                  {years.map((year) => (
                    <TouchableOpacity
                      key={year}
                      style={[styles.datePickerItem, tempYear === year && styles.datePickerItemActive]}
                      onPress={() => setTempYear(year)}
                    >
                      <Text style={[styles.datePickerItemText, tempYear === year && styles.datePickerItemTextActive]}>
                        {year}년
                      </Text>
                    </TouchableOpacity>
                  ))}
                </ScrollView>

                <ScrollView style={styles.datePickerColumn} showsVerticalScrollIndicator={false}>
                  {months.map((month) => (
                    <TouchableOpacity
                      key={month}
                      style={[styles.datePickerItem, tempMonth === month && styles.datePickerItemActive]}
                      onPress={() => setTempMonth(month)}
                    >
                      <Text style={[styles.datePickerItemText, tempMonth === month && styles.datePickerItemTextActive]}>
                        {month}월
                      </Text>
                    </TouchableOpacity>
                  ))}
                </ScrollView>

                <ScrollView style={styles.datePickerColumn} showsVerticalScrollIndicator={false}>
                  {days.map((day) => (
                    <TouchableOpacity
                      key={day}
                      style={[styles.datePickerItem, tempDay === day && styles.datePickerItemActive]}
                      onPress={() => setTempDay(day)}
                    >
                      <Text style={[styles.datePickerItemText, tempDay === day && styles.datePickerItemTextActive]}>
                        {day}일
                      </Text>
                    </TouchableOpacity>
                  ))}
                </ScrollView>
              </View>

              <TouchableOpacity style={styles.datePickerConfirmButton} onPress={handleDateSelect}>
                <Text style={styles.datePickerConfirmText}>확인</Text>
              </TouchableOpacity>
            </View>
          </TouchableOpacity>
        </Modal>
      )}
    </Modal>
  );
};

const styles = StyleSheet.create({
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
    maxHeight: '85%',
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
  scrollContent: {
    maxHeight: 400,
  },
  section: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
    marginBottom: 12,
  },

  // 날짜
  dateRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  dateLabel: {
    fontSize: 15,
    color: '#666',
  },
  dateButton: {
    backgroundColor: '#F2F2F7',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    minWidth: 140,
  },
  dateButtonText: {
    fontSize: 14,
    color: '#000',
    textAlign: 'center',
  },

  // 성별
  genderRow: {
    flexDirection: 'row',
    gap: 12,
  },
  genderButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    backgroundColor: '#F2F2F7',
    alignItems: 'center',
  },
  genderButtonActive: {
    backgroundColor: '#007AFF',
  },
  genderButtonText: {
    fontSize: 15,
    fontWeight: '500',
    color: '#000',
  },
  genderButtonTextActive: {
    color: '#fff',
  },

  // 나이
  ageRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  ageInputContainer: {
    flex: 1,
  },
  ageLabel: {
    fontSize: 13,
    color: '#666',
    marginBottom: 6,
  },
  ageButton: {
    backgroundColor: '#F2F2F7',
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 8,
    marginBottom: 6,
  },
  ageButtonText: {
    fontSize: 14,
    color: '#000',
    textAlign: 'center',
  },
  ageControls: {
    flexDirection: 'row',
    gap: 4,
  },
  ageControlButton: {
    flex: 1,
    backgroundColor: '#007AFF',
    paddingVertical: 6,
    borderRadius: 6,
    alignItems: 'center',
  },
  ageControlText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  ageResetButton: {
    flex: 1,
    backgroundColor: '#FF3B30',
    paddingVertical: 6,
    borderRadius: 6,
    alignItems: 'center',
  },
  ageResetText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#fff',
  },
  ageSeparator: {
    fontSize: 16,
    color: '#8E8E93',
    marginTop: 20,
  },

  // 액션 버튼
  actionButtons: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingTop: 20,
    gap: 12,
  },
  button: {
    flex: 1,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  resetButton: {
    backgroundColor: '#F2F2F7',
  },
  applyButton: {
    backgroundColor: '#007AFF',
  },
  resetButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
  },
  applyButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },

  // 날짜 선택 모달
  datePickerOverlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
  },
  datePickerContent: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    width: '85%',
    maxWidth: 320,
  },
  datePickerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#000',
    textAlign: 'center',
    marginBottom: 16,
  },
  datePickerRow: {
    flexDirection: 'row',
    height: 200,
    gap: 8,
  },
  datePickerColumn: {
    flex: 1,
  },
  datePickerItem: {
    paddingVertical: 10,
    alignItems: 'center',
    borderRadius: 8,
    marginBottom: 4,
  },
  datePickerItemActive: {
    backgroundColor: '#007AFF',
  },
  datePickerItemText: {
    fontSize: 15,
    color: '#000',
  },
  datePickerItemTextActive: {
    color: '#fff',
    fontWeight: '600',
  },
  datePickerConfirmButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 14,
    borderRadius: 10,
    marginTop: 16,
    alignItems: 'center',
  },
  datePickerConfirmText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
});

export default AdvancedFilterModal;
