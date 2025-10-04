import { useState, useEffect } from 'react';
import { projectApi } from '../api';
import type { Project, CreateProjectRequest, UpdateProjectRequest } from '../types';
import toast from 'react-hot-toast';

export const useProjects = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await projectApi.getAll();
      setProjects(data);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to fetch projects';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const createProject = async (data: CreateProjectRequest) => {
    try {
      setIsLoading(true);
      const newProject = await projectApi.create(data);
      setProjects((prev) => [...prev, newProject]);
      toast.success('Project created successfully');
      return newProject;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to create project';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const updateProject = async (id: number, data: UpdateProjectRequest) => {
    try {
      setIsLoading(true);
      const updatedProject = await projectApi.update(id, data);
      setProjects((prev) =>
        prev.map((project) => (project.id === id ? updatedProject : project))
      );
      toast.success('Project updated successfully');
      return updatedProject;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to update project';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const deleteProject = async (id: number) => {
    try {
      setIsLoading(true);
      await projectApi.delete(id);
      setProjects((prev) => prev.filter((project) => project.id !== id));
      toast.success('Project deleted successfully');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to delete project';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  return {
    projects,
    isLoading,
    error,
    fetchProjects,
    createProject,
    updateProject,
    deleteProject,
  };
};

export const useProject = (id: number) => {
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProject = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await projectApi.getById(id);
      setProject(data);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to fetch project';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (id) {
      fetchProject();
    }
  }, [id]);

  return {
    project,
    isLoading,
    error,
    fetchProject,
  };
};