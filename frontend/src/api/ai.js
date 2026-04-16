import { createRequest } from '../utils/request'

// AI service request instance
const aiRequest = createRequest('http://localhost:8003')

export const smartSearchApi = {
  // Smart search - natural language query to structured results
  search(data) {
    return aiRequest.post('/api/ai/smart-search', data)
  },

  // Get search history (future feature)
  getSearchHistory() {
    return aiRequest.get('/api/ai/search-history')
  }
}