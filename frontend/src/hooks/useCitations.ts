import { useState, useEffect } from 'react';
import { citationApi, bibliographyApi } from '../api';
import type { 
  Citation, 
  CreateCitationRequest, 
  UpdateCitationRequest,
  BibliographyRequest,
  BibliographyResponse 
} from '../types';
import toast from 'react-hot-toast';

export const useCitations = (projectId: number) => {
  const [citations, setCitations] = useState<Citation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCitations = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await citationApi.getByProject(projectId);
      setCitations(data);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to fetch citations';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const createCitation = async (data: CreateCitationRequest) => {
    try {
      setIsLoading(true);
      const newCitation = await citationApi.create(projectId, data);
      setCitations((prev) => [...prev, newCitation]);
      toast.success('Citation created successfully');
      return newCitation;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to create citation';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const updateCitation = async (citationId: number, data: UpdateCitationRequest) => {
    try {
      setIsLoading(true);
      const updatedCitation = await citationApi.update(projectId, citationId, data);
      setCitations((prev) =>
        prev.map((citation) => (citation.id === citationId ? updatedCitation : citation))
      );
      toast.success('Citation updated successfully');
      return updatedCitation;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to update citation';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const deleteCitation = async (citationId: number) => {
    try {
      setIsLoading(true);
      await citationApi.delete(projectId, citationId);
      setCitations((prev) => prev.filter((citation) => citation.id !== citationId));
      toast.success('Citation deleted successfully');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to delete citation';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (projectId) {
      fetchCitations();
    }
  }, [projectId]);

  return {
    citations,
    isLoading,
    error,
    fetchCitations,
    createCitation,
    updateCitation,
    deleteCitation,
  };
};

export const useBibliography = () => {
  const [bibliography, setBibliography] = useState<BibliographyResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateBibliography = async (projectId: number, params: BibliographyRequest) => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await bibliographyApi.generate(projectId, params);
      setBibliography(data);
      return data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to generate bibliography';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const clearBibliography = () => {
    setBibliography(null);
    setError(null);
  };

  return {
    bibliography,
    isLoading,
    error,
    generateBibliography,
    clearBibliography,
  };
};