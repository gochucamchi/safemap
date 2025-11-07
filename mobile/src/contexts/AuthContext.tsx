import React, { createContext, useState, useContext, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface AuthContextType {
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // 앱 시작 시 저장된 인증 상태 확인
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const authToken = await AsyncStorage.getItem('auth_token');
      setIsAuthenticated(!!authToken);
    } catch (error) {
      console.log('Error checking auth status:', error);
    }
  };

  // 간단한 로그인 (실제 프로덕션에서는 백엔드 인증 사용)
  const login = async (username: string, password: string): Promise<boolean> => {
    // 데모용 하드코드된 자격증명
    // 실제 프로덕션에서는 백엔드 API로 인증해야 합니다
    if (username === 'admin' && password === 'safemap2024') {
      try {
        await AsyncStorage.setItem('auth_token', 'demo_token');
        setIsAuthenticated(true);
        return true;
      } catch (error) {
        console.log('Error saving auth token:', error);
        return false;
      }
    }
    return false;
  };

  const logout = async () => {
    try {
      await AsyncStorage.removeItem('auth_token');
      setIsAuthenticated(false);
    } catch (error) {
      console.log('Error removing auth token:', error);
    }
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
