import React, { useState } from 'react';
import { PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import type { Citation } from '../types';
import ConfirmDialog from './ConfirmDialog';

interface CitationTableProps {
  citations: Citation[];
  onEdit: (citation: Citation) => void;
  onDelete: (citationId: number) => Promise<void>;
  isLoading?: boolean;
}

const CitationTable: React.FC<CitationTableProps> = ({
  citations,
  onEdit,
  onDelete,
  isLoading = false,
}) => {
  const [deleteConfirm, setDeleteConfirm] = useState<{
    isOpen: boolean;
    citation: Citation | null;
  }>({
    isOpen: false,
    citation: null,
  });
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (citation: Citation) => {
    setDeleteConfirm({
      isOpen: true,
      citation,
    });
  };

  const handleDeleteConfirm = async () => {
    if (!deleteConfirm.citation) return;
    
    try {
      setIsDeleting(true);
      await onDelete(deleteConfirm.citation.id);
      setDeleteConfirm({ isOpen: false, citation: null });
    } finally {
      setIsDeleting(false);
    }
  };

  const formatAuthors = (authors: string[] | null) => {
    if (!authors || authors.length === 0) return 'Unknown';
    if (authors.length === 1) return authors[0];
    if (authors.length === 2) return authors.join(' and ');
    return `${authors[0]} et al.`;
  };

  const formatYear = (year: number | null) => {
    return year ? year.toString() : 'n.d.';
  };

  if (citations.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500">
          <p className="text-lg mb-2">No citations yet</p>
          <p className="text-sm">Create your first citation to get started</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
        <table className="min-w-full divide-y divide-gray-300 bg-white">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Title
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Authors
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Year
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {citations.map((citation) => (
              <tr key={citation.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900 max-w-xs truncate">
                    {citation.title}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900 max-w-xs truncate">
                    {formatAuthors(citation.authors)}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {formatYear(citation.year)}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`
                    inline-flex px-2 py-1 text-xs font-semibold rounded-full
                    ${citation.type === 'book' ? 'bg-blue-100 text-blue-800' : ''}
                    ${citation.type === 'article' ? 'bg-green-100 text-green-800' : ''}
                    ${citation.type === 'website' ? 'bg-purple-100 text-purple-800' : ''}
                    ${citation.type === 'report' ? 'bg-orange-100 text-orange-800' : ''}
                  `}>
                    {citation.type.charAt(0).toUpperCase() + citation.type.slice(1)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex justify-end space-x-2">
                    <button
                      onClick={() => onEdit(citation)}
                      disabled={isLoading}
                      className="text-primary-600 hover:text-primary-900 p-1 rounded-md hover:bg-primary-50 disabled:opacity-50"
                      title="Edit citation"
                    >
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteClick(citation)}
                      disabled={isLoading}
                      className="text-red-600 hover:text-red-900 p-1 rounded-md hover:bg-red-50 disabled:opacity-50"
                      title="Delete citation"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={deleteConfirm.isOpen}
        onClose={() => setDeleteConfirm({ isOpen: false, citation: null })}
        onConfirm={handleDeleteConfirm}
        title="Delete Citation"
        message={`Are you sure you want to delete "${deleteConfirm.citation?.title}"? This action cannot be undone.`}
        confirmText="Delete"
        isLoading={isDeleting}
      />
    </>
  );
};

export default CitationTable;