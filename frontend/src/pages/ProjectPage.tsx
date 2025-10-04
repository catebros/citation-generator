import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PlusIcon, PencilIcon, TrashIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { useProject, useProjects } from '../hooks/useProjects';
import { useCitations, useBibliography } from '../hooks/useCitations';
import CitationTable from '../components/CitationTable';
import CitationFormModal from '../components/CitationFormModal';
import BibliographyModal from '../components/BibliographyModal';
import CreateProjectModal from '../components/CreateProjectModal';
import ConfirmDialog from '../components/ConfirmDialog';
import LoadingSpinner from '../components/LoadingSpinner';
import type { Citation } from '../types';

const ProjectPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const projectId = parseInt(id || '0');
  
  const { project, isLoading: projectLoading, fetchProject } = useProject(projectId);
  const { deleteProject, updateProject } = useProjects();
  const {
    citations,
    isLoading: citationsLoading,
    createCitation,
    updateCitation,
    deleteCitation,
  } = useCitations(projectId);
  const { generateBibliography } = useBibliography();

  // Modal states
  const [isCitationModalOpen, setIsCitationModalOpen] = useState(false);
  const [isEditProjectModalOpen, setIsEditProjectModalOpen] = useState(false);
  const [isBibliographyModalOpen, setIsBibliographyModalOpen] = useState(false);
  const [editingCitation, setEditingCitation] = useState<Citation | null>(null);
  const [deleteProjectConfirm, setDeleteProjectConfirm] = useState(false);
  
  // Loading states
  const [isCitationSaving, setIsCitationSaving] = useState(false);
  const [isProjectUpdating, setIsProjectUpdating] = useState(false);
  const [isProjectDeleting, setIsProjectDeleting] = useState(false);

  const handleCreateCitation = async (data: any) => {
    try {
      setIsCitationSaving(true);
      await createCitation(data);
      setIsCitationModalOpen(false);
    } finally {
      setIsCitationSaving(false);
    }
  };

  const handleEditCitation = (citation: Citation) => {
    setEditingCitation(citation);
    setIsCitationModalOpen(true);
  };

  const handleUpdateCitation = async (data: any) => {
    if (!editingCitation) return;
    
    try {
      setIsCitationSaving(true);
      await updateCitation(editingCitation.id, data);
      setEditingCitation(null);
      setIsCitationModalOpen(false);
    } finally {
      setIsCitationSaving(false);
    }
  };

  const handleDeleteCitation = async (citationId: number) => {
    await deleteCitation(citationId);
  };

  const handleUpdateProject = async (name: string) => {
    try {
      setIsProjectUpdating(true);
      await updateProject(projectId, { name });
      // Refresh the project data to update the UI
      await fetchProject();
      setIsEditProjectModalOpen(false);
    } catch (error) {
      console.error('Error updating project:', error);
      // Re-throw the error so the modal can handle it
      throw error;
    } finally {
      setIsProjectUpdating(false);
    }
  };

  const handleDeleteProject = async () => {
    try {
      setIsProjectDeleting(true);
      await deleteProject(projectId);
      setDeleteProjectConfirm(false);
      navigate('/');
    } catch (error) {
      console.error('Error deleting project:', error);
    } finally {
      setIsProjectDeleting(false);
    }
  };

  const handleGenerateBibliography = async (projectId: number, formatType: 'apa' | 'mla') => {
    return await generateBibliography(projectId, { format_type: formatType });
  };

  const handleCloseCitationModal = () => {
    setIsCitationModalOpen(false);
    setEditingCitation(null);
  };

  if (projectLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading project..." />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Project Not Found</h1>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            Back to Projects
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Header */}
        <div className="mb-8 mt-8">
          <div className="flex items-center justify-between">
            <div>
              <button
                onClick={() => navigate('/')}
                className="inline-flex items-center px-4 py-2 text-base font-medium text-primary-600 bg-primary-50 border border-primary-200 rounded-lg hover:bg-primary-100 hover:text-primary-700 transition-colors duration-200 mb-4"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Back to Projects
              </button>
              <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
              <p className="text-gray-600 mt-2">
                Created: {new Date(project.created_at).toLocaleDateString()}
              </p>
            </div>
            
            <button
              onClick={() => setIsEditProjectModalOpen(true)}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 flex items-center space-x-2"
            >
              <PencilIcon className="h-4 w-4" />
              <span>Edit Project</span>
            </button>
          </div>
        </div>

        {/* Actions Bar */}
        <div className="mb-6 flex items-center justify-between">
          <button
            onClick={() => setIsCitationModalOpen(true)}
            className="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 flex items-center space-x-2"
          >
            <PlusIcon className="h-4 w-4" />
            <span>Create Citation</span>
          </button>

          <button
            onClick={() => setIsBibliographyModalOpen(true)}
            disabled={citations.length === 0}
            className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <DocumentTextIcon className="h-4 w-4" />
            <span>Generate Bibliography</span>
          </button>
        </div>

        {/* Citations Table */}
        <div className="bg-white shadow rounded-lg mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">
              Citations ({citations.length})
            </h2>
          </div>
          <div className="p-6">
            {citationsLoading ? (
              <div className="flex justify-center py-8">
                <LoadingSpinner text="Loading citations..." />
              </div>
            ) : (
              <CitationTable
                citations={citations}
                onEdit={handleEditCitation}
                onDelete={handleDeleteCitation}
                isLoading={citationsLoading}
              />
            )}
          </div>
        </div>

        {/* Delete Project */}
        <div className="border-t pt-8">
          <div className="flex justify-center">
            <button
              onClick={() => setDeleteProjectConfirm(true)}
              className="px-4 py-2 text-sm font-medium text-red-700 bg-red-50 border border-red-200 rounded-md hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-500 flex items-center space-x-2"
            >
              <TrashIcon className="h-4 w-4" />
              <span>Delete Project</span>
            </button>
          </div>
        </div>

        {/* Modals */}
        <CitationFormModal
          isOpen={isCitationModalOpen}
          onClose={handleCloseCitationModal}
          onSubmit={editingCitation ? handleUpdateCitation : handleCreateCitation}
          citation={editingCitation || undefined}
          isLoading={isCitationSaving}
        />

        <CreateProjectModal
          isOpen={isEditProjectModalOpen}
          onClose={() => setIsEditProjectModalOpen(false)}
          onSubmit={handleUpdateProject}
          isLoading={isProjectUpdating}
          isEdit={true}
          initialName={project?.name || ''}
        />

        <BibliographyModal
          isOpen={isBibliographyModalOpen}
          onClose={() => setIsBibliographyModalOpen(false)}
          projectId={projectId}
          onGenerate={handleGenerateBibliography}
        />

        <ConfirmDialog
          isOpen={deleteProjectConfirm}
          onClose={() => setDeleteProjectConfirm(false)}
          onConfirm={handleDeleteProject}
          title="Delete Project"
          message={`Are you sure you want to delete "${project.name}"? This will also delete all citations. This action cannot be undone.`}
          confirmText="Delete Project"
          isLoading={isProjectDeleting}
        />
      </div>
    </div>
  );
};

export default ProjectPage;