import axios from 'axios';
import type {
  Project,
  CreateProjectRequest,
  UpdateProjectRequest,
  Citation,
  CreateCitationRequest,
  UpdateCitationRequest,
  BibliographyRequest,
  BibliographyResponse,
} from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Projects API
export const projectApi = {
  // Get all projects
  getAll: async (): Promise<Project[]> => {
    const response = await api.get('/projects');
    return response.data;
  },

  // Create a new project
  create: async (data: CreateProjectRequest): Promise<Project> => {
    const response = await api.post('/projects', data);
    return response.data;
  },

  // Get a project by ID
  getById: async (id: number): Promise<Project> => {
    const response = await api.get(`/projects/${id}`);
    return response.data;
  },

  // Update a project
  update: async (id: number, data: UpdateProjectRequest): Promise<Project> => {
    const response = await api.put(`/projects/${id}`, data);
    return response.data;
  },

  // Delete a project
  delete: async (id: number): Promise<void> => {
    await api.delete(`/projects/${id}`);
  },
};

// Citations API
export const citationApi = {
  // Get all citations for a project
  getByProject: async (projectId: number): Promise<Citation[]> => {
    const response = await api.get(`/projects/${projectId}/citations`);
    return response.data;
  },

  // Create a new citation
  create: async (
    projectId: number,
    data: CreateCitationRequest
  ): Promise<Citation> => {
    const response = await api.post(`/projects/${projectId}/citations`, data);
    return response.data;
  },

  // Update a citation
  update: async (
    projectId: number,
    citationId: number,
    data: UpdateCitationRequest
  ): Promise<Citation> => {
    const response = await api.put(
      `/projects/${projectId}/citations/${citationId}`,
      data
    );
    return response.data;
  },

  // Delete a citation
  delete: async (projectId: number, citationId: number): Promise<void> => {
    await api.delete(`/projects/${projectId}/citations/${citationId}`);
  },
};

// Bibliography API
export const bibliographyApi = {
  // Generate bibliography
  generate: async (
    projectId: number,
    params: BibliographyRequest
  ): Promise<BibliographyResponse> => {
    const response = await api.get(`/projects/${projectId}/bibliography`, {
      params,
    });
    return response.data;
  },
};

export default api;