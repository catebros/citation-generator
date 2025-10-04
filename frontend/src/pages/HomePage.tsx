import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProjects } from '../hooks/useProjects';
import ProjectCard from '../components/ProjectCard';
import CreateProjectModal from '../components/CreateProjectModal';
import LoadingSpinner from '../components/LoadingSpinner';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { projects, isLoading, createProject } = useProjects();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);

  const handleCreateProject = async (name: string) => {
    try {
      setIsCreating(true);
      const newProject = await createProject({ name });
      setIsCreateModalOpen(false);
      navigate(`/project/${newProject.id}`);
    } catch (error) {
      // Re-throw the error so the modal can handle it
      throw error;
    } finally {
      setIsCreating(false);
    }
  };

  const handleProjectClick = (projectId: number) => {
    navigate(`/project/${projectId}`);
  };

  if (isLoading && projects.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading projects..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        {/* Header */}
        <div className="mb-12 text-center mt-20">
          <h1 className="text-5xl font-bold text-gray-900 mb-3">
            Citation Manager
          </h1>
          <div className="w-24 h-1 bg-gradient-to-r from-primary-500 to-primary-600 mx-auto mb-6 rounded-full"></div>
          <p className="text-2xl text-gray-600 mb-3">Welcome back!</p>
          <p className="text-lg text-gray-500">Your projects:</p>
        </div>

        {/* Projects Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {/* Create Project Card */}
          <ProjectCard
            isCreateCard
            onClick={() => setIsCreateModalOpen(true)}
          />

          {/* Project Cards */}
          {projects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onClick={() => handleProjectClick(project.id)}
            />
          ))}
        </div>

        {/* Empty State */}
        {projects.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <div className="text-gray-500">
              <p className="text-lg mb-2">No projects yet</p>
              <p className="text-sm">Create your first project to get started</p>
            </div>
          </div>
        )}

        {/* Create Project Modal */}
        <CreateProjectModal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          onSubmit={handleCreateProject}
          isLoading={isCreating}
        />
      </div>
    </div>
  );
};

export default HomePage;