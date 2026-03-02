import axios from 'axios'

export const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 5000,
})

export async function fetchProjects() {
  const response = await apiClient.get('/projects')
  return response.data
}