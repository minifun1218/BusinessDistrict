<template>
  <div class="city-selector">
    <div class="selector-trigger" @click="showSelector = !showSelector">
      <div class="current-city">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M21 10C21 17 12 23 12 23S3 17 3 10C3 5.02944 7.02944 1 12 1C16.9706 1 21 5.02944 21 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="12" cy="10" r="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span>{{ selectedCity.name || '选择城市' }}</span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" :class="{ 'rotate': showSelector }">
          <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
    </div>

    <div v-if="showSelector" class="selector-panel modern-card fade-in">
      <!-- 搜索框 -->
      <div class="search-section">
        <div class="search-input-wrapper">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
            <path d="M21 21L16.65 16.65" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索城市名称"
            class="search-input"
            @input="handleSearch"
          />
          <button v-if="searchKeyword" @click="clearSearch" class="clear-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </div>



      <!-- 搜索结果 -->
      <div v-if="searchKeyword && searchResults.length > 0" class="search-results">
        <div class="section-title">搜索结果</div>
        <div class="city-list">
          <div
            v-for="city in searchResults"
            :key="city.id"
            class="city-item"
            :class="{ active: selectedCity.id === city.id }"
            @click="selectCity(city)"
          >
            <div class="city-name">{{ city.name }}</div>
            <div class="city-info">{{ city.parentName }} · {{ formatPopulation(city.population) }}</div>
          </div>
        </div>
      </div>

      <!-- 热门城市 -->
      <div v-if="!searchKeyword" class="hot-cities">
        <div class="section-title">热门城市</div>
        <div class="city-grid">
          <div
            v-for="city in hotCities"
            :key="city.id"
            class="city-tag"
            :class="{ active: selectedCity.id === city.id }"
            @click="selectCity(city)"
          >
            {{ city.name }}
          </div>
        </div>
      </div>

      <!-- 城市列表 -->
      <div v-if="!searchKeyword" class="city-list-section">
        <div class="section-title">
          全部城市
          <span v-if="allCities.length > 0" class="city-count">({{ allCities.length }}个)</span>
        </div>
        <div class="alphabet-nav">
          <div
            v-for="letter in alphabet"
            :key="letter"
            class="alphabet-item"
            :class="{ 
              active: currentLetter === letter,
              'has-cities': cityGroups.some(g => g.letter === letter)
            }"
            @click="scrollToLetter(letter)"
          >
            {{ letter }}
          </div>
        </div>
        
        <div class="cities-by-letter" ref="cityListRef">
          <div
            v-for="group in cityGroups"
            :key="group.letter"
            :data-letter="group.letter"
            class="letter-group"
          >
            <div class="letter-title">
              {{ group.letter }}
              <span class="letter-count">({{ group.cities.length }})</span>
            </div>
            <div class="city-list">
              <div
                v-for="city in group.cities"
                :key="city.id"
                class="city-item"
                :class="{ active: selectedCity.id === city.id }"
                @click="selectCity(city)"
              >
                <div class="city-name">{{ city.name }}</div>
                <div class="city-info">{{ city.parentName }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-section">
        <div class="modern-loading"></div>
        <span>加载中...</span>
      </div>
    </div>

    <!-- 遮罩层 -->
    <div v-if="showSelector" class="selector-overlay" @click="showSelector = false"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { cityApi } from '../api/city.js'

// Props
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'change', 'location-found'])

// 响应式数据
const showSelector = ref(false)
const loading = ref(false)
const locating = ref(false)
const searchKeyword = ref('')
const currentLetter = ref('A')
const cityListRef = ref(null)

const selectedCity = ref(props.modelValue || {})
const hotCities = ref([])
const allCities = ref([])
const searchResults = ref([])
const currentLocation = ref(null)

// 字母表
const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')

// 生成拼音首字母的辅助函数
const generatePinyin = (name) => {
  // 简单的城市名称到拼音的映射
  const cityPinyinMap = {
    '北京': 'beijing', '上海': 'shanghai', '广州': 'guangzhou', '深圳': 'shenzhen',
    '杭州': 'hangzhou', '南京': 'nanjing', '武汉': 'wuhan', '成都': 'chengdu',
    '天津': 'tianjin', '重庆': 'chongqing', '苏州': 'suzhou', '西安': 'xian',
    '青岛': 'qingdao', '郑州': 'zhengzhou', '大连': 'dalian', '厦门': 'xiamen',
    '济南': 'jinan', '宁波': 'ningbo', '石家庄': 'shijiazhuang', '沈阳': 'shenyang',
    '长沙': 'changsha', '昆明': 'kunming', '福州': 'fuzhou', '无锡': 'wuxi',
    '合肥': 'hefei', '哈尔滨': 'harbin', '长春': 'changchun', '温州': 'wenzhou',
    '佛山': 'foshan', '东莞': 'dongguan', '太原': 'taiyuan', '南昌': 'nanchang'
  }
  
  return cityPinyinMap[name] || name.toLowerCase()
}

// 计算属性
const cityGroups = computed(() => {
  if (!allCities.value.length) return []
  
  console.log('开始生成城市分组，总城市数:', allCities.value.length)
  
  const groups = {}
  
  allCities.value.forEach(city => {
    let firstLetter = 'Z' // 默认分组
    
    if (city.pinyin) {
      // 使用拼音首字母
      firstLetter = city.pinyin[0].toUpperCase()
    } else if (city.name) {
      // 根据城市名称生成拼音
      const pinyin = generatePinyin(city.name)
      firstLetter = pinyin[0].toUpperCase()
    }
    
    // 确保首字母是有效的字母
    if (!/^[A-Z]$/.test(firstLetter)) {
      firstLetter = 'Z'
    }
    
    if (!groups[firstLetter]) {
      groups[firstLetter] = []
    }
    groups[firstLetter].push(city)
  })
  
  // 按字母排序并统计
  const sortedGroups = Object.keys(groups).sort().map(letter => ({
    letter,
    cities: groups[letter].sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'))
  }))
  
  console.log('城市分组结果:', sortedGroups.map(g => `${g.letter}: ${g.cities.length}个`).join(', '))
  
  return sortedGroups
})

// 监听props变化
watch(() => props.modelValue, (newValue) => {
  selectedCity.value = newValue || {}
}, { deep: true })

// 方法
const loadHotCities = async () => {
  try {
    console.log('开始加载热门城市...')
    const data = await cityApi.getHotCities()
    console.log('热门城市API返回数据:', data)
    
    // 处理不同的数据格式
    let cities = []
    if (data && data.success && data.data) {
      cities = Array.isArray(data.data) ? data.data : []
    } else if (Array.isArray(data)) {
      cities = data
    } else {
      cities = []
    }
    
    hotCities.value = cities
      .filter(city => city && city.name)
      .map(city => ({
        id: city.id || city.city_id || `hot_${Math.random().toString(36).substr(2, 9)}`,
        name: city.name,
        pinyin: city.pinyin || city.pinyin_full || generatePinyin(city.name),
        pinyin_abbr: city.pinyin_abbr || city.pinyin_short || '',
        parentName: city.parent_name || city.province_name || city.province || '',
        population: city.population || 0,
        level: city.level || 'city',
        longitude: city.longitude || city.lng,
        latitude: city.latitude || city.lat,
        isHot: true // 标记为热门城市
      }))
    
    console.log('处理后的热门城市:', hotCities.value.length, '个城市')
    
    // 如果没有热门城市数据，使用默认数据
    if (hotCities.value.length === 0) {
      console.log('API未返回热门城市，使用默认数据')
      hotCities.value = getDefaultHotCities()
    }
  } catch (error) {
    console.error('加载热门城市失败:', error)
    // 如果API失败，使用默认热门城市
    hotCities.value = getDefaultHotCities()
  }
}

const loadAllCities = async () => {
  try {
    loading.value = true
    console.log('开始加载所有城市...')
    
    const data = await cityApi.getCityList({ 
      level: 'city',
      pageSize: 1000,  // 获取更多城市数据
      _t: Date.now()   // 添加时间戳避免缓存
    })
    console.log('城市列表API返回数据:', data)
    
    // 处理不同的数据格式
    let cities = []
    if (data && data.success && data.data) {
      // 标准响应格式 {success: true, data: {items: [...], total: 100}}
      if (data.data.items && Array.isArray(data.data.items)) {
        cities = data.data.items
      } else if (Array.isArray(data.data)) {
        cities = data.data
      }
    } else if (data && data.items && Array.isArray(data.items)) {
      // 直接分页格式 {items: [...], total: 100}
      cities = data.items
    } else if (Array.isArray(data)) {
      // 直接数组格式 [...]
      cities = data
    } else {
      console.warn('未识别的城市数据格式:', data)
      cities = []
    }
    
    console.log('解析出的城市数据:', cities.length, '个城市')
    
    // 数据映射和清理
    allCities.value = cities
      .filter(city => city && city.name) // 过滤无效数据
      .map(city => ({
        id: city.id || city.city_id || `city_${Math.random().toString(36).substr(2, 9)}`,
        name: city.name,
        pinyin: city.pinyin || city.pinyin_full || generatePinyin(city.name),
        pinyin_abbr: city.pinyin_abbr || city.pinyin_short || '',
        parentName: city.parent_name || city.province_name || city.province || '',
        population: city.population || 0,
        level: city.level || 'city',
        longitude: city.longitude || city.lng,
        latitude: city.latitude || city.lat
      }))
      .sort((a, b) => {
        // 按拼音排序，确保首字母分组正确
        const pinyinA = a.pinyin || a.name
        const pinyinB = b.pinyin || b.name
        return pinyinA.localeCompare(pinyinB, 'zh-CN', { sensitivity: 'base' })
      })
    
    console.log('处理并排序后的城市列表:', allCities.value.length, '个城市')
    console.log('首批城市示例:', allCities.value.slice(0, 5))
  } catch (error) {
    console.error('加载城市列表失败:', error)
    // 如果API失败，使用默认城市列表
    allCities.value = getDefaultCities()
  } finally {
    loading.value = false
  }
}

const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    searchResults.value = []
    return
  }
  
  try {
    console.log('搜索城市:', searchKeyword.value)
    const data = await cityApi.searchCities(searchKeyword.value)
    console.log('搜索API返回结果:', data)
    
    // 处理搜索结果数据格式
    let cities = []
    if (data && data.success && data.data) {
      cities = Array.isArray(data.data) ? data.data : []
    } else if (Array.isArray(data)) {
      cities = data
    } else {
      cities = []
    }
    
    searchResults.value = cities
      .filter(city => city && city.name)
      .map(city => ({
        id: city.id || city.city_id || `search_${Math.random().toString(36).substr(2, 9)}`,
        name: city.name,
        pinyin: city.pinyin || city.pinyin_full || generatePinyin(city.name),
        pinyin_abbr: city.pinyin_abbr || city.pinyin_short || '',
        parentName: city.parent_name || city.province_name || city.province || '',
        population: city.population || 0,
        level: city.level || 'city',
        longitude: city.longitude || city.lng,
        latitude: city.latitude || city.lat
      }))
      .sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'))
    
    console.log('处理后的搜索结果:', searchResults.value.length, '个城市')
  } catch (error) {
    console.error('搜索城市失败:', error)
    searchResults.value = []
  }
}

const clearSearch = () => {
  searchKeyword.value = ''
  searchResults.value = []
}

const getCurrentLocation = async () => {
  if (!navigator.geolocation) {
    alert('您的浏览器不支持地理定位')
    return
  }
  
  locating.value = true
  
  navigator.geolocation.getCurrentPosition(
    async (position) => {
      try {
        const { longitude, latitude } = position.coords
        console.log('获取到坐标:', longitude, latitude)
        
        const data = await cityApi.getCityByLocation(longitude, latitude)
        console.log('定位城市数据:', data)
        
        // 处理定位城市数据格式
        if (data) {
          const locationCity = {
            id: data.id || `location_${Date.now()}`,
            name: data.name,
            pinyin: data.pinyin || data.pinyin_full || generatePinyin(data.name),
            pinyin_abbr: data.pinyin_abbr || data.pinyin_short || '',
            parentName: data.parent_name || data.province_name || data.province || '',
            population: data.population || 0,
            longitude: longitude,
            latitude: latitude
          }
          
          currentLocation.value = locationCity
          
          // 发出定位事件，包含坐标信息
          emit('location-found', {
            city: locationCity,
            coordinates: { longitude, latitude }
          })
          
          selectCity(locationCity)
        } else {
          // 即使没有城市数据，也可以发出坐标信息
          console.warn('未获取到城市数据，但有坐标信息')
          emit('location-found', {
            city: null,
            coordinates: { longitude, latitude }
          })
        }
      } catch (error) {
        console.error('获取定位城市失败:', error)
        alert('获取定位信息失败')
      } finally {
        locating.value = false
      }
    },
    (error) => {
      console.error('定位失败:', error)
      alert('定位失败，请检查定位权限')
      locating.value = false
    },
    {
      timeout: 10000,
      enableHighAccuracy: true
    }
  )
}

const selectCity = (city) => {
  selectedCity.value = city
  emit('update:modelValue', city)
  emit('change', city)
  showSelector.value = false
}

const scrollToLetter = (letter) => {
  // 检查该字母下是否有城市
  const hasCity = cityGroups.value.some(group => group.letter === letter)
  if (!hasCity) {
    console.log(`字母 ${letter} 下没有城市，跳过滚动`)
    return
  }
  
  currentLetter.value = letter
  const element = cityListRef.value?.querySelector(`[data-letter="${letter}"]`)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
    console.log(`滚动到字母 ${letter}`)
  } else {
    console.warn(`找不到字母 ${letter} 对应的元素`)
  }
}

const formatPopulation = (population) => {
  if (!population) return ''
  if (population >= 10000) {
    return `${(population / 10000).toFixed(1)}万人`
  }
  return `${population}人`
}

// 默认热门城市数据（API失败时使用）
const getDefaultHotCities = () => {
  return [
    { id: 'beijing', name: '北京', pinyin: 'beijing', pinyin_abbr: 'BJ', parentName: '北京市', population: 21542000 },
    { id: 'shanghai', name: '上海', pinyin: 'shanghai', pinyin_abbr: 'SH', parentName: '上海市', population: 26317104 },
    { id: 'guangzhou', name: '广州', pinyin: 'guangzhou', pinyin_abbr: 'GZ', parentName: '广东省', population: 15906000 },
    { id: 'shenzhen', name: '深圳', pinyin: 'shenzhen', pinyin_abbr: 'SZ', parentName: '广东省', population: 13438800 },
    { id: 'hangzhou', name: '杭州', pinyin: 'hangzhou', pinyin_abbr: 'HZ', parentName: '浙江省', population: 12196000 },
    { id: 'nanjing', name: '南京', pinyin: 'nanjing', pinyin_abbr: 'NJ', parentName: '江苏省', population: 9423400 },
    { id: 'wuhan', name: '武汉', pinyin: 'wuhan', pinyin_abbr: 'WH', parentName: '湖北省', population: 13648000 },
    { id: 'chengdu', name: '成都', pinyin: 'chengdu', pinyin_abbr: 'CD', parentName: '四川省', population: 21192000 }
  ]
}

// 默认城市列表数据（API失败时使用）
const getDefaultCities = () => {
  return [
    ...getDefaultHotCities(),
    { id: 'tianjin', name: '天津', pinyin: 'tianjin', pinyin_abbr: 'TJ', parentName: '天津市', population: 15618000 },
    { id: 'chongqing', name: '重庆', pinyin: 'chongqing', pinyin_abbr: 'CQ', parentName: '重庆市', population: 32054159 },
    { id: 'suzhou', name: '苏州', pinyin: 'suzhou', pinyin_abbr: 'SZ', parentName: '江苏省', population: 12952000 },
    { id: 'xian', name: '西安', pinyin: 'xian', pinyin_abbr: 'XA', parentName: '陕西省', population: 12952907 },
    { id: 'qingdao', name: '青岛', pinyin: 'qingdao', pinyin_abbr: 'QD', parentName: '山东省', population: 10071722 },
    { id: 'zhengzhou', name: '郑州', pinyin: 'zhengzhou', pinyin_abbr: 'ZZ', parentName: '河南省', population: 12600574 },
    { id: 'dalian', name: '大连', pinyin: 'dalian', pinyin_abbr: 'DL', parentName: '辽宁省', population: 7450785 },
    { id: 'xiamen', name: '厦门', pinyin: 'xiamen', pinyin_abbr: 'XM', parentName: '福建省', population: 5163970 },
    { id: 'jinan', name: '济南', pinyin: 'jinan', pinyin_abbr: 'JN', parentName: '山东省', population: 9202432 },
    { id: 'ningbo', name: '宁波', pinyin: 'ningbo', pinyin_abbr: 'NB', parentName: '浙江省', population: 9404283 }
  ]
}

// 生命周期
onMounted(() => {
  loadHotCities()
  loadAllCities()
})
</script>

<style scoped>
.city-selector {
  position: relative;
}

.selector-trigger {
  cursor: pointer;
}

.current-city {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #374151;
  border: 1px solid #4b5563;
  border-radius: 8px;
  color: #f3f4f6;
  transition: all 0.3s ease;
  min-width: 120px;
}

.current-city:hover {
  background: #4b5563;
  border-color: #60a5fa;
}

.current-city svg:last-child {
  margin-left: auto;
  transition: transform 0.3s ease;
}

.current-city svg:last-child.rotate {
  transform: rotate(180deg);
}

.selector-panel {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  min-width: 400px;
  max-width: 500px;
  max-height: 600px;
  background: rgba(31, 41, 55, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(75, 85, 99, 0.3);
  border-radius: 16px;
  padding: 20px;
  z-index: 1000;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.selector-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 999;
}

.search-section {
  margin-bottom: 20px;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input-wrapper svg:first-child {
  position: absolute;
  left: 12px;
  color: #9ca3af;
  z-index: 2;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 40px;
  background: #374151;
  border: 1px solid #4b5563;
  border-radius: 8px;
  color: #f9fafb;
  font-size: 14px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #60a5fa;
  background: #4b5563;
}

.search-input::placeholder {
  color: #9ca3af;
}

.clear-btn {
  position: absolute;
  right: 8px;
  padding: 4px;
  background: #4b5563;
  border: none;
  border-radius: 4px;
  color: #9ca3af;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-btn:hover {
  background: #6b7280;
  color: #f3f4f6;
}

.location-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #4b5563;
}

.location-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #374151;
  border: 1px solid #4b5563;
  border-radius: 8px;
  color: #f3f4f6;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.location-btn:hover:not(:disabled) {
  background: #4b5563;
  border-color: #60a5fa;
}

.location-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.current-location {
  margin-top: 8px;
  padding: 10px 12px;
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 8px;
  color: #f3f4f6;
}

.location-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 4px;
}

.location-info svg {
  color: #22c55e;
  flex-shrink: 0;
}

.location-coordinates {
  font-size: 11px;
  color: #9ca3af;
  font-family: 'Courier New', monospace;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #f3f4f6;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.city-count {
  font-size: 12px;
  color: #9ca3af;
  font-weight: 400;
}

.hot-cities {
  margin-bottom: 20px;
}

.city-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 8px;
}

.city-tag {
  padding: 8px 12px;
  background: #374151;
  border: 1px solid #4b5563;
  border-radius: 6px;
  color: #f3f4f6;
  font-size: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.city-tag:hover {
  background: #4b5563;
  border-color: #60a5fa;
}

.city-tag.active {
  background: rgba(59, 130, 246, 0.3);
  border-color: #3b82f6;
}

.search-results,
.city-list-section {
  max-height: 300px;
  overflow-y: auto;
}

.alphabet-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 16px;
  padding: 12px;
  background: #374151;
  border-radius: 8px;
}

.alphabet-item {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #9ca3af;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.alphabet-item:hover {
  background: #4b5563;
  color: #f3f4f6;
}

.alphabet-item.active {
  background: rgba(59, 130, 246, 0.3);
  color: #f3f4f6;
}

.alphabet-item.has-cities {
  color: #f3f4f6;
  font-weight: 500;
}

.alphabet-item:not(.has-cities) {
  opacity: 0.5;
  cursor: not-allowed;
}

.letter-group {
  margin-bottom: 16px;
}

.letter-title {
  font-size: 14px;
  font-weight: 600;
  color: #e5e7eb;
  margin-bottom: 8px;
  padding: 4px 8px;
  background: #374151;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.letter-count {
  font-size: 11px;
  color: #9ca3af;
  font-weight: 400;
  background: rgba(156, 163, 175, 0.1);
  padding: 2px 6px;
  border-radius: 8px;
}

.city-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.city-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #374151;
  border: 1px solid #4b5563;
  margin-bottom: 4px;
}

.city-item:hover {
  background: #4b5563;
  border-color: #60a5fa;
}

.city-item.active {
  background: rgba(59, 130, 246, 0.2);
  border-color: #3b82f6;
}

.city-name {
  font-size: 14px;
  font-weight: 500;
  color: #f3f4f6;
  margin-bottom: 2px;
}

.city-info {
  font-size: 12px;
  color: #d1d5db;
}

.loading-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: #d1d5db;
}

/* 滚动条样式 */
.search-results::-webkit-scrollbar,
.city-list-section::-webkit-scrollbar,
.cities-by-letter::-webkit-scrollbar {
  width: 6px;
}

.search-results::-webkit-scrollbar-track,
.city-list-section::-webkit-scrollbar-track,
.cities-by-letter::-webkit-scrollbar-track {
  background: #374151;
  border-radius: 3px;
}

.search-results::-webkit-scrollbar-thumb,
.city-list-section::-webkit-scrollbar-thumb,
.cities-by-letter::-webkit-scrollbar-thumb {
  background: #60a5fa;
  border-radius: 3px;
}

.search-results::-webkit-scrollbar-thumb:hover,
.city-list-section::-webkit-scrollbar-thumb:hover,
.cities-by-letter::-webkit-scrollbar-thumb:hover {
  background: #3b82f6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .selector-panel {
    min-width: 300px;
    max-width: 90vw;
  }
  
  .city-grid {
    grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
  }
  
  .alphabet-nav {
    gap: 2px;
  }
  
  .alphabet-item {
    width: 20px;
    height: 20px;
    font-size: 10px;
  }
}
</style>
