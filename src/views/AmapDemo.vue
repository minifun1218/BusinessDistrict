<template>
  <div class="amap-demo">
    <div class="demo-header">
      <h1>高德地图组件演示</h1>
      <p>基于高德地图API v2.0的Vue3组件，支持POI搜索、坐标获取、商圈查询等功能</p>
    </div>
    
    <div class="demo-content">
      <!-- 高德地图组件 -->
      <AmapMap
        v-model="mapCenter"
        :height="'70vh'"
        :business-areas="businessAreas"
        :current-city="selectedCity"
        @poi-selected="handlePOISelected"
        @area-selected="handleAreaSelected"
        @location-changed="handleLocationChanged"
        @city-changed="handleCityChange"
      />
      
      <!-- 信息面板 -->
      <div class="info-panel">
        <h3>操作说明</h3>
        <ul>
          <li>🔍 在搜索框输入关键字搜索POI（如：北京大学、三里屯、咖啡厅）</li>
          <li>📍 点击地图任意位置获取坐标并搜索附近商圈</li>
          <li>🏙️ 使用城市选择器切换不同城市</li>
          <li>📋 点击搜索结果或地图标记查看详情</li>
          <li>📱 支持分页浏览更多搜索结果</li>
        </ul>
        
        <div class="current-info" v-if="currentCoords">
          <h4>当前坐标</h4>
          <p>经度: {{ currentCoords.lng.toFixed(6) }}</p>
          <p>纬度: {{ currentCoords.lat.toFixed(6) }}</p>
        </div>
        
        <div class="selected-info" v-if="selectedPOI">
          <h4>选中POI</h4>
          <p><strong>名称:</strong> {{ selectedPOI.name }}</p>
          <p><strong>地址:</strong> {{ selectedPOI.address }}</p>
          <p><strong>类型:</strong> {{ selectedPOI.type }}</p>
          <p v-if="selectedPOI.tel"><strong>电话:</strong> {{ selectedPOI.tel }}</p>
        </div>
        
        <div class="selected-area" v-if="selectedArea">
          <h4>选中商圈</h4>
          <p><strong>名称:</strong> {{ selectedArea.name }}</p>
          <p><strong>类型:</strong> {{ selectedArea.category }}</p>
          <p><strong>热度:</strong> {{ selectedArea.hotValue }}</p>
          <p v-if="selectedArea.distance"><strong>距离:</strong> {{ selectedArea.distance }}米</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AmapMap from '@/components/AmapMap.vue'

// 响应式数据
const mapCenter = ref({ lng: 116.4074, lat: 39.9042 })
const selectedCity = ref({ id: 'beijing', name: '北京' })
const currentCoords = ref(null)
const selectedPOI = ref(null)
const selectedArea = ref(null)

// 模拟商圈数据
const businessAreas = ref([
  {
    id: '1',
    name: '王府井商业街',
    category: '购物中心',
    hotValue: 95,
    longitude: 116.4103,
    latitude: 39.9107,
    storeCount: 200,
    avgConsumption: 350
  },
  {
    id: '2',
    name: '三里屯太古里',
    category: '时尚街区',
    hotValue: 92,
    longitude: 116.4566,
    latitude: 39.9342,
    storeCount: 150,
    avgConsumption: 280
  },
  {
    id: '3',
    name: '中关村',
    category: '科技商圈',
    hotValue: 88,
    longitude: 116.3119,
    latitude: 39.9555,
    storeCount: 180,
    avgConsumption: 200
  },
  {
    id: '4',
    name: '国贸CBD',
    category: '商务区',
    hotValue: 90,
    longitude: 116.4576,
    latitude: 39.9081,
    storeCount: 120,
    avgConsumption: 400
  },
  {
    id: '5',
    name: '西单商圈',
    category: '购物中心',
    hotValue: 85,
    longitude: 116.3751,
    latitude: 39.9059,
    storeCount: 160,
    avgConsumption: 250
  }
])

// 事件处理函数
const handlePOISelected = (poi) => {
  console.log('选中POI:', poi)
  selectedPOI.value = poi
  selectedArea.value = null
}

const handleAreaSelected = (area) => {
  console.log('选中商圈:', area)
  selectedArea.value = area
  selectedPOI.value = null
}

const handleLocationChanged = (coords) => {
  console.log('位置变化:', coords)
  currentCoords.value = coords
  
  if (coords.nearbyAreas && coords.nearbyAreas.length > 0) {
    console.log('附近商圈:', coords.nearbyAreas)
  }
}

const handleCityChange = (city) => {
  console.log('城市切换:', city)
  selectedCity.value = city
  selectedPOI.value = null
  selectedArea.value = null
}
</script>

<style scoped>
.amap-demo {
  padding: 20px;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.demo-header {
  text-align: center;
  margin-bottom: 30px;
  color: white;
}

.demo-header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.demo-header p {
  font-size: 1.1rem;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

.demo-content {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.info-panel {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  height: fit-content;
}

.info-panel h3 {
  margin: 0 0 15px 0;
  color: #2d3748;
  font-size: 1.2rem;
}

.info-panel ul {
  margin: 0 0 20px 0;
  padding-left: 0;
  list-style: none;
}

.info-panel li {
  margin-bottom: 8px;
  padding: 8px 12px;
  background: #f7fafc;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.4;
  color: #4a5568;
}

.current-info,
.selected-info,
.selected-area {
  margin-top: 20px;
  padding: 15px;
  background: #edf2f7;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.current-info h4,
.selected-info h4,
.selected-area h4 {
  margin: 0 0 10px 0;
  color: #2d3748;
  font-size: 1rem;
}

.current-info p,
.selected-info p,
.selected-area p {
  margin: 5px 0;
  font-size: 13px;
  color: #4a5568;
  line-height: 1.4;
}

.selected-info p strong,
.selected-area p strong {
  color: #2d3748;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .demo-content {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .info-panel {
    order: -1;
  }
  
  .demo-header h1 {
    font-size: 2rem;
  }
  
  .demo-header p {
    font-size: 1rem;
  }
}

@media (max-width: 768px) {
  .amap-demo {
    padding: 15px;
  }
  
  .demo-header h1 {
    font-size: 1.8rem;
  }
  
  .info-panel {
    padding: 15px;
  }
  
  .info-panel li {
    font-size: 13px;
    padding: 6px 10px;
  }
}
</style>
