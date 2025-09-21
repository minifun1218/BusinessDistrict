// API响应基础结构
export const ApiResponse = {
  code: 0,
  message: '',
  data: null,
  timestamp: 0
}

// 城市信息类型
export const CityInfo = {
  id: '',
  name: '',
  code: '',
  level: '', // 'province' | 'city' | 'district'
  parentId: '',
  longitude: 0,
  latitude: 0,
  population: 0,
  area: 0,
  economicLevel: '', // 'high' | 'medium' | 'low'
  isHot: false
}

// 商圈信息类型
export const BusinessArea = {
  id: '',
  name: '',
  cityId: '',
  type: '', // 'shopping' | 'dining' | 'entertainment' | 'mixed'
  level: '', // 'A' | 'B' | 'C' | 'D'
  longitude: 0,
  latitude: 0,
  area: 0, // 平方公里
  hotValue: 0, // 热度值
  avgConsumption: 0, // 平均消费
  customerFlow: 0, // 日均客流量
  storeCount: 0, // 店铺数量
  rating: 0, // 评分
  address: '',
  description: '',
  facilities: [], // 配套设施
  transportation: [], // 交通信息
  openingHours: '',
  images: [],
  tags: []
}

// 店铺信息类型
export const Store = {
  id: '',
  name: '',
  businessAreaId: '',
  category: '', // 'restaurant' | 'retail' | 'entertainment' | 'service'
  subCategory: '',
  longitude: 0,
  latitude: 0,
  rating: 0,
  reviewCount: 0,
  avgPrice: 0,
  phone: '',
  address: '',
  openingHours: '',
  description: '',
  images: [],
  tags: [],
  facilities: [],
  isRecommended: false
}

// 用户信息类型
export const UserInfo = {
  id: '',
  username: '',
  email: '',
  phone: '',
  avatar: '',
  nickname: '',
  gender: '', // 'male' | 'female' | 'unknown'
  age: 0,
  city: '',
  preferences: [], // 用户偏好
  vipLevel: 0,
  points: 0,
  createdAt: '',
  updatedAt: ''
}

// 统计数据类型
export const StatisticsData = {
  // 商圈热度排行
  hotRanking: [],
  
  // 时段客流分析
  hourlyFlow: {
    hours: [],
    weekday: [],
    weekend: []
  },
  
  // 消费类型分布
  categoryDistribution: [],
  
  // 情感分析
  sentimentAnalysis: {
    positive: 0,
    neutral: 0,
    negative: 0
  },
  
  // 消费趋势
  consumptionTrend: {
    dates: [],
    sales: [],
    customers: []
  },
  
  // 商圈对比
  areaComparison: {
    indicators: [],
    data: []
  }
}

// 搜索参数类型
export const SearchParams = {
  keyword: '',
  cityId: '',
  longitude: 0,
  latitude: 0,
  radius: 1000, // 米
  category: '',
  minRating: 0,
  maxPrice: 0,
  sortBy: '', // 'distance' | 'rating' | 'price' | 'popularity'
  sortOrder: 'asc', // 'asc' | 'desc'
  page: 1,
  pageSize: 20
}

// 分页响应类型
export const PaginatedResponse = {
  list: [],
  total: 0,
  page: 1,
  pageSize: 20,
  totalPages: 0,
  hasNext: false,
  hasPrev: false
}

// 登录请求参数
export const LoginParams = {
  username: '', // 邮箱或手机号
  password: '',
  remember: false,
  captcha: '',
  captchaId: ''
}

// 注册请求参数
export const RegisterParams = {
  username: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
  captcha: '',
  captchaId: '',
  inviteCode: ''
}

// 认证响应
export const AuthResponse = {
  accessToken: '',
  refreshToken: '',
  expiresIn: 0,
  tokenType: 'Bearer',
  user: null // UserInfo
}
