// Types for the Citation Generator API

export interface Project {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectRequest {
  name: string;
}

export interface UpdateProjectRequest {
  name: string;
}

export interface Citation {
  id: number;
  project_id: number;
  type: CitationType;
  title: string;
  authors: string[] | null;
  year: number | null;
  publisher: string | null;
  place: string | null;
  journal: string | null;
  volume: number | null;
  issue: string | null;
  pages: string | null;
  url: string | null;
  access_date: string | null;
  doi: string | null;
  edition: number | null;
  created_at: string;
  updated_at: string;
}

export type CitationType = 'book' | 'article' | 'website' | 'report';

export interface CreateCitationRequest {
  type: CitationType;
  title: string;
  authors?: string[];
  year?: number | null;
  publisher?: string;
  place?: string;
  journal?: string;
  volume?: number;
  issue?: string;
  pages?: string;
  url?: string;
  access_date?: string;
  doi?: string;
  edition?: number;
}

export interface UpdateCitationRequest extends CreateCitationRequest {}

export interface BibliographyRequest {
  format_type: 'apa' | 'mla';
}

export interface BibliographyResponse {
  bibliography: string[];
  format_type: string;
}

export interface ApiError {
  detail: string;
}

export interface LoadingState {
  isLoading: boolean;
  error: string | null;
}