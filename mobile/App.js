import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import { Text } from 'react-native';

// 화면 컴포넌트들
import MapScreen from './src/screens/MapScreen';
import ListScreen from './src/screens/ListScreen';
import StatsScreen from './src/screens/StatsScreen';

const Tab = createBottomTabNavigator();

// 간단한 아이콘 컴포넌트 (Ionicons 대체)
function TabIcon({ label, focused }) {
  const icons = {
    '지도': '🗺️',
    '목록': '📋',
    '통계': '📊'
  };
  return <Text style={{ fontSize: 24 }}>{icons[label]}</Text>;
}

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ focused }) => {
            const labels = {
              'Map': '지도',
              'List': '목록', 
              'Stats': '통계'
            };
            return <TabIcon label={labels[route.name]} focused={focused} />;
          },
          tabBarActiveTintColor: '#007AFF',
          tabBarInactiveTintColor: 'gray',
          tabBarStyle: {
            paddingBottom: 5,
            paddingTop: 5,
            height: 60,
          },
          headerStyle: {
            backgroundColor: '#007AFF',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        })}
      >
        <Tab.Screen
          name="Map"
          component={MapScreen}
          options={{
            tabBarLabel: '지도',
            headerTitle: 'SafeMap - 안전지도',
          }}
        />
        <Tab.Screen
          name="List"
          component={ListScreen}
          options={{
            tabBarLabel: '목록',
            headerTitle: '실종 사건 목록',
          }}
        />
        <Tab.Screen
          name="Stats"
          component={StatsScreen}
          options={{
            tabBarLabel: '통계',
            headerTitle: '통계 및 분석',
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
