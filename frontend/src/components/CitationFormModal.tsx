import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BookOpenIcon, 
  DocumentTextIcon, 
  GlobeAltIcon, 
  DocumentChartBarIcon 
} from '@heroicons/react/24/outline';
import Modal from './Modal';
import LoadingSpinner from './LoadingSpinner';
import type { Citation, CitationType, CreateCitationRequest, UpdateCitationRequest } from '../types';

interface CitationFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateCitationRequest | UpdateCitationRequest) => Promise<void>;
  citation?: Citation;
  isLoading?: boolean;
}

const CITATION_TYPES = [
  { type: 'book' as CitationType, label: 'Book', icon: BookOpenIcon },
  { type: 'article' as CitationType, label: 'Article', icon: DocumentTextIcon },
  { type: 'website' as CitationType, label: 'Website', icon: GlobeAltIcon },
  { type: 'report' as CitationType, label: 'Report', icon: DocumentChartBarIcon },
];

const CitationFormModal: React.FC<CitationFormModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  citation,
  isLoading = false,
}) => {
  const [selectedType, setSelectedType] = useState<CitationType>('book');
  const [formData, setFormData] = useState({
    title: '',
    authors: [] as string[],
    year: '',
    publisher: '',
    place: '',
    journal: '',
    volume: '',
    issue: '',
    pages: '',
    url: '',
    access_date: '',
    doi: '',
    edition: '',
  });
  const [yearIsNone, setYearIsNone] = useState(false);
  const [authorInput, setAuthorInput] = useState('');

  // Initialize form with citation data for editing
  useEffect(() => {
    if (citation) {
      setSelectedType(citation.type);
      setFormData({
        title: citation.title || '',
        authors: citation.authors || [],
        year: citation.year ? citation.year.toString() : '',
        publisher: citation.publisher || '',
        place: citation.place || '',
        journal: citation.journal || '',
        volume: citation.volume ? citation.volume.toString() : '',
        issue: citation.issue || '',
        pages: citation.pages || '',
        url: citation.url || '',
        access_date: citation.access_date || '',
        doi: citation.doi || '',
        edition: citation.edition ? citation.edition.toString() : '',
      });
      setYearIsNone(citation.year === null);
      setAuthorInput((citation.authors || []).join(', '));
    }
  }, [citation]);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleAuthorInputChange = (value: string) => {
    setAuthorInput(value);
    const authors = value.split(',').map(author => author.trim()).filter(Boolean);
    setFormData(prev => ({ ...prev, authors }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const submitData: CreateCitationRequest | UpdateCitationRequest = {
      type: selectedType,
      title: formData.title,
      authors: formData.authors.length > 0 ? formData.authors : undefined,
      year: yearIsNone ? null : (formData.year ? parseInt(formData.year) : undefined),
      publisher: formData.publisher || undefined,
      place: formData.place || undefined,
      journal: formData.journal || undefined,
      volume: formData.volume ? parseInt(formData.volume) : undefined,
      issue: formData.issue || undefined,
      pages: formData.pages || undefined,
      url: formData.url || undefined,
      access_date: formData.access_date || undefined,
      doi: formData.doi || undefined,
      edition: formData.edition ? parseInt(formData.edition) : undefined,
    };

    try {
      await onSubmit(submitData);
      handleClose();
    } catch (err) {
      // Error handling is done in the hook
    }
  };

  const handleClose = () => {
    setSelectedType('book');
    setFormData({
      title: '',
      authors: [],
      year: '',
      publisher: '',
      place: '',
      journal: '',
      volume: '',
      issue: '',
      pages: '',
      url: '',
      access_date: '',
      doi: '',
      edition: '',
    });
    setYearIsNone(false);
    setAuthorInput('');
    onClose();
  };

  const renderFieldsForType = () => {
    const commonFields = (
      <>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              className="form-input"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Authors
            </label>
            <input
              type="text"
              value={authorInput}
              onChange={(e) => handleAuthorInputChange(e.target.value)}
              placeholder="Separate multiple authors with commas"
              className="form-input"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Year
            </label>
            <div className="space-y-2">
              <input
                type="number"
                value={formData.year}
                onChange={(e) => handleInputChange('year', e.target.value)}
                disabled={yearIsNone}
                className="form-input disabled:bg-gray-100"
              />
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={yearIsNone}
                  onChange={(e) => setYearIsNone(e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-600">Year is None</span>
              </label>
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Publisher
            </label>
            <input
              type="text"
              value={formData.publisher}
              onChange={(e) => handleInputChange('publisher', e.target.value)}
              className="form-input"
            />
          </div>
        </div>
      </>
    );

    const typeSpecificFields = () => {
      switch (selectedType) {
        case 'book':
          return (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Place
                </label>
                <input
                  type="text"
                  value={formData.place}
                  onChange={(e) => handleInputChange('place', e.target.value)}
                  className="form-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Edition
                </label>
                <input
                  type="number"
                  value={formData.edition}
                  onChange={(e) => handleInputChange('edition', e.target.value)}
                  className="form-input"
                />
              </div>
            </div>
          );
        
        case 'article':
          return (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Journal
                </label>
                <input
                  type="text"
                  value={formData.journal}
                  onChange={(e) => handleInputChange('journal', e.target.value)}
                  className="form-input"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Volume
                  </label>
                  <input
                    type="number"
                    value={formData.volume}
                    onChange={(e) => handleInputChange('volume', e.target.value)}
                    className="form-input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Issue
                  </label>
                  <input
                    type="text"
                    value={formData.issue}
                    onChange={(e) => handleInputChange('issue', e.target.value)}
                    className="form-input"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Pages
                  </label>
                  <input
                    type="text"
                    value={formData.pages}
                    onChange={(e) => handleInputChange('pages', e.target.value)}
                    placeholder="e.g., 123-145"
                    className="form-input"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  DOI
                </label>
                <input
                  type="text"
                  value={formData.doi}
                  onChange={(e) => handleInputChange('doi', e.target.value)}
                  placeholder="e.g., 10.1234/example.doi"
                  className="form-input"
                />
              </div>
            </>
          );
        
        case 'website':
          return (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  URL
                </label>
                <input
                  type="url"
                  value={formData.url}
                  onChange={(e) => handleInputChange('url', e.target.value)}
                  className="form-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Access Date
                </label>
                <input
                  type="date"
                  value={formData.access_date}
                  onChange={(e) => handleInputChange('access_date', e.target.value)}
                  className="form-input"
                />
              </div>
            </>
          );
        
        case 'report':
          return (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                URL
              </label>
              <input
                type="url"
                value={formData.url}
                onChange={(e) => handleInputChange('url', e.target.value)}
                className="form-input"
              />
            </div>
          );
        
        default:
          return null;
      }
    };

    return (
      <div className="space-y-4">
        {commonFields}
        {typeSpecificFields()}
      </div>
    );
  };

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={handleClose} 
      title={citation ? 'Edit Citation' : 'Create Citation'}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Citation Type Selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Citation Type
          </label>
          <div className="grid grid-cols-4 gap-3">
            {CITATION_TYPES.map(({ type, label, icon: Icon }) => (
              <motion.button
                key={type}
                type="button"
                onClick={() => setSelectedType(type)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`
                  p-3 rounded-lg border-2 transition-all duration-200 flex flex-col items-center space-y-2
                  ${selectedType === type 
                    ? 'border-primary-500 bg-primary-50 text-primary-700' 
                    : 'border-gray-200 hover:border-gray-300 text-gray-600'
                  }
                `}
              >
                <Icon className="h-6 w-6" />
                <span className="text-sm font-medium">{label}</span>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Form Fields */}
        {renderFieldsForType()}

        {/* Submit Buttons */}
        <div className="flex justify-end space-x-3 pt-4 border-t">
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
            disabled={isLoading || !formData.title.trim()}
            className="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 flex items-center space-x-2"
          >
            {isLoading && <LoadingSpinner size="sm" />}
            <span>{isLoading ? 'Saving...' : (citation ? 'Update' : 'Create')}</span>
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default CitationFormModal;
