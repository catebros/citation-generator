import React from 'react';
import { motion } from 'framer-motion';
import { PlusIcon, FolderIcon } from '@heroicons/react/24/outline';
import type { Project } from '../types';

interface ProjectCardProps {
  project?: Project;
  isCreateCard?: boolean;
  onClick: () => void;
}

const ProjectCard: React.FC<ProjectCardProps> = ({ 
  project, 
  isCreateCard = false, 
  onClick 
}) => {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`
        relative p-6 rounded-lg border-2 cursor-pointer transition-all duration-200
        ${isCreateCard 
          ? 'border-dashed border-gray-300 hover:border-primary-400 hover:bg-primary-50' 
          : 'border-gray-200 bg-white hover:border-primary-300 hover:shadow-md'
        }
      `}
    >
      {isCreateCard ? (
        <div className="flex flex-col items-center justify-center h-32 text-gray-500">
          <PlusIcon className="h-12 w-12 mb-2" />
          <span className="text-lg font-medium">Create Project</span>
        </div>
      ) : (
        <div className="flex flex-col h-32">
          <div className="flex items-start justify-between mb-4">
            <FolderIcon className="h-8 w-8 text-primary-600" />
          </div>
          
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
              {project?.name}
            </h3>
            
            <div className="text-sm text-gray-500">
              Created: {project?.created_at ? new Date(project.created_at).toLocaleDateString() : 'Unknown'}
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default ProjectCard;