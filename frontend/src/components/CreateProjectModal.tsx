import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import Modal from './Modal';
import LoadingSpinner from './LoadingSpinner';

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (name: string) => Promise<void>;
  isLoading?: boolean;
  isEdit?: boolean;
  initialName?: string;
}

const CreateProjectModal: React.FC<CreateProjectModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
  isEdit = false,
  initialName = '',
}) => {
  const [projectName, setProjectName] = useState(initialName);
  const [error, setError] = useState('');

  // Update the project name when the modal opens or initialName changes
  useEffect(() => {
    if (isOpen) {
      setProjectName(initialName);
      setError('');
    }
  }, [isOpen, initialName]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!projectName.trim()) {
      setError('Project name is required');
      return;
    }

    // Check if nothing has changed in edit mode
    if (isEdit && projectName.trim() === initialName.trim()) {
      toast('No changes detected', {
        icon: '❌',
        duration: 3000,
      });
      return;
    }

    try {
      setError('');
      await onSubmit(projectName.trim());
      // Only clear and close if no error occurred
      if (!isEdit) {
        setProjectName('');
      }
      onClose();
    } catch (err: any) {
      // Don't show error in modal since the hook already shows toast notification
      // Just don't close the modal so user can fix the error
    }
  };

  const handleClose = () => {
    if (!isEdit) {
      setProjectName('');
    }
    setError('');
    onClose();
  };

  const modalTitle = isEdit ? 'Edit Project' : 'Create New Project';
  const submitButtonText = isEdit ? 'Update' : 'Create';
  const loadingText = isEdit ? 'Updating...' : 'Creating...';

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title={modalTitle}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="projectName" className="block text-sm font-medium text-gray-700 mb-1">
            Project Name
          </label>
          <input
            type="text"
            id="projectName"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            className="form-input"
            placeholder="Enter project name..."
            disabled={isLoading}
            autoFocus
          />
          {error && (
            <p className="mt-1 text-sm text-red-600">{error}</p>
          )}
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={handleClose}
            disabled={isLoading}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading || !projectName.trim()}
            className="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 flex items-center space-x-2"
          >
            {isLoading && <LoadingSpinner size="sm" />}
            <span>{isLoading ? loadingText : submitButtonText}</span>
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default CreateProjectModal;