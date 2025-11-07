import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';

export default function ProfileScreen({ navigation }: any) {
  const { isAuthenticated, logout } = useAuth();

  const handleLogout = () => {
    Alert.alert(
      '로그아웃',
      '로그아웃 하시겠습니까?',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '로그아웃',
          style: 'destructive',
          onPress: async () => {
            await logout();
            Alert.alert('로그아웃', '로그아웃 되었습니다');
          },
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.logo}>🗺️</Text>
        <Text style={styles.title}>SafeMap</Text>
        <Text style={styles.subtitle}>실종자 정보 지도 서비스</Text>
      </View>

      <View style={styles.content}>
        {isAuthenticated ? (
          // 로그인된 상태
          <View>
            <View style={styles.statusCard}>
              <View style={styles.statusIcon}>
                <Text style={styles.statusEmoji}>✅</Text>
              </View>
              <Text style={styles.statusTitle}>로그인 됨</Text>
              <Text style={styles.statusText}>
                실종 해제자의 상세 정보를{'\n'}
                열람할 수 있습니다
              </Text>
            </View>

            <TouchableOpacity
              style={styles.logoutButton}
              onPress={handleLogout}
            >
              <Text style={styles.logoutButtonText}>로그아웃</Text>
            </TouchableOpacity>
          </View>
        ) : (
          // 로그아웃된 상태
          <View>
            <View style={styles.statusCard}>
              <View style={styles.statusIcon}>
                <Text style={styles.statusEmoji}>🔒</Text>
              </View>
              <Text style={styles.statusTitle}>로그인 필요</Text>
              <Text style={styles.statusText}>
                실종 해제자의 상세 정보를 보려면{'\n'}
                로그인이 필요합니다
              </Text>
            </View>

            <TouchableOpacity
              style={styles.loginButton}
              onPress={() => navigation.navigate('Login')}
            >
              <Text style={styles.loginButtonText}>로그인</Text>
            </TouchableOpacity>

            <View style={styles.infoBox}>
              <Text style={styles.infoTitle}>개인정보 보호</Text>
              <Text style={styles.infoText}>
                실종 해제된 경우 개인정보 보호를 위해{'\n'}
                상세 정보 열람이 제한됩니다.
              </Text>
              <Text style={styles.infoText} style={{ marginTop: 12 }}>
                실종 중인 경우 수색을 위해{'\n'}
                모든 정보가 공개됩니다.
              </Text>
            </View>
          </View>
        )}

        <View style={styles.versionBox}>
          <Text style={styles.versionText}>버전 1.0.0</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    backgroundColor: '#fff',
    paddingTop: 60,
    paddingBottom: 30,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  logo: {
    fontSize: 60,
    marginBottom: 12,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  statusCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statusIcon: {
    marginBottom: 12,
  },
  statusEmoji: {
    fontSize: 48,
  },
  statusTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 8,
  },
  statusText: {
    fontSize: 15,
    color: '#666',
    textAlign: 'center',
    lineHeight: 22,
  },
  loginButton: {
    backgroundColor: '#007AFF',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginBottom: 20,
  },
  loginButtonText: {
    color: '#fff',
    fontSize: 17,
    fontWeight: '600',
  },
  logoutButton: {
    backgroundColor: '#FF3B30',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginBottom: 20,
  },
  logoutButtonText: {
    color: '#fff',
    fontSize: 17,
    fontWeight: '600',
  },
  infoBox: {
    backgroundColor: '#F2F2F7',
    borderRadius: 12,
    padding: 16,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  versionBox: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20,
    alignItems: 'center',
  },
  versionText: {
    fontSize: 13,
    color: '#999',
  },
});
