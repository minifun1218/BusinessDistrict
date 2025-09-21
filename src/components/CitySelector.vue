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

      <!-- 当前定位 -->
      <div class="location-section">
        <button @click="getCurrentLocation" class="location-btn" :disabled="locating">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C13.1046 2 14 2.89543 14 4C14 5.10457 13.1046 6 12 6C10.8954 6 10 5.10457 10 4C10 2.89543 10.8954 2 12 2Z" fill="currentColor"/>
            <path d="M12 22C13.1046 22 14 21.1046 14 20C14 18.8954 13.1046 18 12 18C10.8954 18 10 18.8954 10 20C10 21.1046 10.8954 22 12 22Z" fill="currentColor"/>
            <path d="M2 12C2 13.1046 2.89543 14 4 14C5.10457 14 6 13.1046 6 12C6 10.8954 5.10457 10 4 10C2.89543 10 2 10.8954 2 12Z" fill="currentColor"/>
            <path d="M22 12C22 13.1046 21.1046 14 20 14C18.8954 14 18 13.1046 18 12C18 10.8954 18.8954 10 20 10C21.1046 10 22 10.8954 22 12Z" fill="currentColor"/>
            <path d="M12 8V16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M8 12H16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span v-if="locating" class="modern-loading"></span>
          {{ locating ? '定位中...' : '当前定位' }}
        </button>
        <div v-if="currentLocation" class="current-location">
          <span>{{ currentLocation.name }}</span>
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
        <div class="section-title">全部城市</div>
        <div class="alphabet-nav">
          <div
            v-for="letter in alphabet"
            :key="letter"
            class="alphabet-item"
            :class="{ active: currentLetter === letter }"
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
            <div class="letter-title">{{ group.letter }}</div>
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
import { cityApi } from '../api/city'

// Props
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'change'])

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

// 计算属性
const cityGroups = computed(() => {
  if (!allCities.value.length) return []
  
  const groups = {}
  allCities.value.forEach(city => {
    const firstLetter = city.pinyin ? city.pinyin[0].toUpperCase() : 'Z'
    if (!groups[firstLetter]) {
      groups[firstLetter] = []
    }
    groups[firstLetter].push(city)
  })
  
  return Object.keys(groups).sort().map(letter => ({
    letter,
    cities: groups[letter]
  }))
})

// 监听props变化
watch(() => props.modelValue, (newValue) => {
  selectedCity.value = newValue || {}
}, { deep: true })

// 方法
const loadHotCities = async () => {
  try {
    const data = await cityApi.getHotCities()
    hotCities.value = data || []
  } catch (error) {
    console.error('加载热门城市失败:', error)
  }
}

const loadAllCities = async () => {
  try {
    loading.value = true
    const data = await cityApi.getCityList({ level: 'city' })
    allCities.value = data || []
  } catch (error) {
    console.error('加载城市列表失败:', error)
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
    const data = await cityApi.searchCities(searchKeyword.value)
    searchResults.value = data || []
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
        const data = await cityApi.getCityByLocation(longitude, latitude)
        currentLocation.value = data
        if (data) {
          selectCity(data)
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
  currentLetter.value = letter
  const element = cityListRef.value?.querySelector(`[data-letter="${letter}"]`)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
  }
}

const formatPopulation = (population) => {
  if (!population) return ''
  if (population >= 10000) {
    return `${(population / 10000).toFixed(1)}万人`
  }
  return `${population}人`
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
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #fff;
  transition: all 0.3s ease;
  min-width: 120px;
}

.current-city:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
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
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 20px;
  z-index: 1000;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
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
  color: rgba(255, 255, 255, 0.6);
  z-index: 2;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 40px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.15);
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.clear-btn {
  position: absolute;
  right: 8px;
  padding: 4px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.location-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.location-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.location-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.location-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.current-location {
  margin-top: 8px;
  padding: 8px 12px;
  background: rgba(102, 126, 234, 0.2);
  border-radius: 6px;
  color: #fff;
  font-size: 12px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 12px;
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
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: #fff;
  font-size: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.city-tag:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.city-tag.active {
  background: rgba(102, 126, 234, 0.3);
  border-color: #667eea;
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
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.alphabet-item {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.alphabet-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.alphabet-item.active {
  background: rgba(102, 126, 234, 0.3);
  color: #fff;
}

.letter-group {
  margin-bottom: 16px;
}

.letter-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 8px;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
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
}

.city-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.city-item.active {
  background: rgba(102, 126, 234, 0.2);
}

.city-name {
  font-size: 14px;
  font-weight: 500;
  color: #fff;
  margin-bottom: 2px;
}

.city-info {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.loading-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: rgba(255, 255, 255, 0.7);
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
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.search-results::-webkit-scrollbar-thumb,
.city-list-section::-webkit-scrollbar-thumb,
.cities-by-letter::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.5);
  border-radius: 3px;
}

.search-results::-webkit-scrollbar-thumb:hover,
.city-list-section::-webkit-scrollbar-thumb:hover,
.cities-by-letter::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.7);
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
