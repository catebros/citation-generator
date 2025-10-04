import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BookOpenIcon, 
  DocumentTextIcon, 
  GlobeAltIcon, 
  DocumentChartBarIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import Modal from './Modal';
import LoadingSpinner from './LoadingSpinner';
import type { Citation, CitationType, CreateCitationRequest, UpdateCitationRequest } from '../types';
import { getInlineErrorMessage, type ParsedErrors } from '../utils/errorParser';

interface CitationFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateCitationRequest | UpdateCitationRequest) => Promise<void>;
  citation?: Citation;
  isLoading?: boolean;
  validationErrors?: ParsedErrors;
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
  validationErrors = { fieldErrors: {}, generalError: null },
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
  const [authorFields, setAuthorFields] = useState<string[]>(['']); // Dynamic author fields
  const [authorErrors, setAuthorErrors] = useState<Record<number, string>>({}); // Track errors by index
  const [yearValidationError, setYearValidationError] = useState<string | null>(null); // Year validation error
  
  // Track original data for comparison (only for editing)
  const [originalData, setOriginalData] = useState<any>(null);

  // Helper function to get required fields for each citation type
  const getRequiredFields = (citationType: CitationType): string[] => {
    const requiredFieldsMap: Record<CitationType, string[]> = {
      book: ["type", "title", "authors", "year", "publisher", "place", "edition"],
      article: ["type", "title", "authors", "year", "journal", "volume", "issue", "pages", "doi"],
      website: ["type", "title", "authors", "year", "publisher", "url", "access_date"],
      report: ["type", "title", "authors", "year", "publisher", "url", "place"]
    };
    return requiredFieldsMap[citationType] || [];
  };

  // Helper function to get ALL valid fields for each citation type (required + optional)
  const getValidFields = (citationType: CitationType): string[] => {
    const validFieldsMap: Record<CitationType, string[]> = {
      book: ["type", "title", "authors", "year", "publisher", "place", "edition"],
      article: ["type", "title", "authors", "year", "journal", "volume", "issue", "pages", "doi"],
      website: ["type", "title", "authors", "year", "publisher", "url", "access_date"],
      report: ["type", "title", "authors", "year", "publisher", "url", "place"]
    };
    return validFieldsMap[citationType] || [];
  };

  // Helper function to filter data by valid fields for the selected type
  const filterByValidFields = (data: any, citationType: CitationType): any => {
    const validFields = getValidFields(citationType);
    const filtered: any = {};
    
    // Only include fields that are valid for this citation type
    Object.keys(data).forEach(field => {
      if (validFields.includes(field)) {
        filtered[field] = data[field];
      }
    });
    
    return filtered;
  };

  // Helper function to validate year field
  const validateYear = (): boolean => {
    // Clear previous error
    setYearValidationError(null);
    
    // If yearIsNone is NOT checked but there's no year value, that's an error
    if (!yearIsNone && (!formData.year || formData.year.trim() === '')) {
      setYearValidationError('Year is required. Either enter a year or check "Year is None"');
      return false;
    }
    
    // If yearIsNone is checked, it's valid
    if (yearIsNone) {
      return true;
    }
    
    // If there's a year value, validate it's a valid number
    if (formData.year && formData.year.trim() !== '') {
      const yearNum = parseInt(formData.year);
      if (isNaN(yearNum) || yearNum < 1000 || yearNum > new Date().getFullYear() + 10) {
        setYearValidationError('Please enter a valid year');
        return false;
      }
    }
    
    return true;
  };

  // Helper function to prepare data for CREATE mode
  const getCreateData = () => {
    const currentAuthors = authorFields.filter(author => author.trim() !== '');
    const currentYear = yearIsNone ? null : (formData.year ? parseInt(formData.year) : null);
    const currentVolume = formData.volume ? parseInt(formData.volume) : null;
    const currentEdition = formData.edition ? parseInt(formData.edition) : null;

    // First, collect all data that has values
    const allData: any = {
      type: selectedType
    };

    // Add all fields that have data
    if (formData.title?.trim()) {
      allData.title = formData.title.trim();
    }
    
    if (currentAuthors.length > 0) {
      allData.authors = currentAuthors;
    }
    
    // Always include year (null if yearIsNone is checked, otherwise the number or null)
    allData.year = currentYear;
    
    if (formData.publisher?.trim()) {
      allData.publisher = formData.publisher.trim();
    }
    
    if (formData.place?.trim()) {
      allData.place = formData.place.trim();
    }
    
    if (formData.journal?.trim()) {
      allData.journal = formData.journal.trim();
    }
    
    if (currentVolume !== null) {
      allData.volume = currentVolume;
    }
    
    if (formData.issue?.trim()) {
      allData.issue = formData.issue.trim();
    }
    
    if (formData.pages?.trim()) {
      allData.pages = formData.pages.trim();
    }
    
    if (formData.url?.trim()) {
      allData.url = formData.url.trim();
    }
    
    if (formData.access_date?.trim()) {
      allData.access_date = formData.access_date.trim();
    }
    
    if (formData.doi?.trim()) {
      allData.doi = formData.doi.trim();
    }
    
    if (currentEdition !== null) {
      allData.edition = currentEdition;
    }

    // Filter by valid fields for the selected citation type
    const filteredData = filterByValidFields(allData, selectedType);
    
    console.log('CREATE - All collected data:', allData);
    console.log('CREATE - Valid fields for', selectedType, ':', getValidFields(selectedType));
    console.log('CREATE - Filtered data:', filteredData);

    return filteredData;
  };

  // Helper function to prepare data for UPDATE mode
  const getUpdateData = () => {
    if (!originalData) {
      console.error('No original data for update mode');
      return {};
    }

    const currentAuthors = authorFields.filter(author => author.trim() !== '');
    const currentYear = yearIsNone ? null : (formData.year ? parseInt(formData.year) : null);
    const currentVolume = formData.volume ? parseInt(formData.volume) : null;
    const currentEdition = formData.edition ? parseInt(formData.edition) : null;

    const allChanges: any = {};

    // Always check type first
    if (selectedType !== originalData.type) {
      allChanges.type = selectedType;
    }

    // Check all fields for changes - including cases where user switched types and back
    const currentTitle = formData.title?.trim() || '';
    if (currentTitle !== (originalData.title || '')) {
      allChanges.title = currentTitle || null;
    }

    const originalAuthors = originalData.authors || [];
    if (JSON.stringify(currentAuthors) !== JSON.stringify(originalAuthors)) {
      allChanges.authors = currentAuthors;
    }

    if (currentYear !== originalData.year) {
      allChanges.year = currentYear;
    }

    const currentPublisher = formData.publisher?.trim() || '';
    if (currentPublisher !== (originalData.publisher || '')) {
      allChanges.publisher = currentPublisher || null;
    }

    const currentPlace = formData.place?.trim() || '';
    if (currentPlace !== (originalData.place || '')) {
      allChanges.place = currentPlace || null;
    }

    const currentJournal = formData.journal?.trim() || '';
    if (currentJournal !== (originalData.journal || '')) {
      allChanges.journal = currentJournal || null;
    }

    if (currentVolume !== originalData.volume) {
      allChanges.volume = currentVolume;
    }

    const currentIssue = formData.issue?.trim() || '';
    if (currentIssue !== (originalData.issue || '')) {
      allChanges.issue = currentIssue || null;
    }

    const currentPages = formData.pages?.trim() || '';
    if (currentPages !== (originalData.pages || '')) {
      allChanges.pages = currentPages || null;
    }

    const currentUrl = formData.url?.trim() || '';
    if (currentUrl !== (originalData.url || '')) {
      allChanges.url = currentUrl || null;
    }

    const currentAccessDate = formData.access_date?.trim() || '';
    if (currentAccessDate !== (originalData.access_date || '')) {
      allChanges.access_date = currentAccessDate || null;
    }

    const currentDoi = formData.doi?.trim() || '';
    if (currentDoi !== (originalData.doi || '')) {
      allChanges.doi = currentDoi || null;
    }

    if (currentEdition !== originalData.edition) {
      allChanges.edition = currentEdition;
    }

    // Filter changes by valid fields for the selected citation type
    const filteredChanges = filterByValidFields(allChanges, selectedType);
    
    console.log('UPDATE - All detected changes:', allChanges);
    console.log('UPDATE - Valid fields for', selectedType, ':', getValidFields(selectedType));
    console.log('UPDATE - Filtered changes:', filteredChanges);

    return filteredChanges;
  };

  // Main function to get data for submission
  const getSubmissionData = () => {
    if (!citation || !originalData) {
      // CREATE MODE
      return getCreateData();
    } else {
      // UPDATE MODE
      return getUpdateData();
    }
  };

  // Helper function to get inline error for a field
  const getFieldError = (fieldName: string): string | null => {
    const error = validationErrors.fieldErrors[fieldName];
    return error ? getInlineErrorMessage(fieldName, error) : null;
  };

  // Initialize form with citation data for editing
  useEffect(() => {
    if (citation) {
      setSelectedType(citation.type);
      const initialFormData = {
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
      };
      setFormData(initialFormData);
      
      // Store original data for comparison
      setOriginalData({
        type: citation.type,
        title: citation.title,
        authors: citation.authors,
        year: citation.year,
        publisher: citation.publisher,
        place: citation.place,
        journal: citation.journal,
        volume: citation.volume,
        issue: citation.issue,
        pages: citation.pages,
        url: citation.url,
        access_date: citation.access_date,
        doi: citation.doi,
        edition: citation.edition,
      });
      
      // Set yearIsNone based on whether the original year is null
      setYearIsNone(citation.year === null);
      
      // Initialize author fields from existing authors
      const authors = citation.authors || [];
      if (authors.length > 0) {
        setAuthorFields([...authors, '']); // Add empty field at the end
      } else {
        setAuthorFields(['']);
      }
    } else {
      // Reset original data for new citations
      setOriginalData(null);
    }
  }, [citation]);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  // Handle dynamic author fields
  const handleAuthorChange = (index: number, value: string) => {
    const newFields = [...authorFields];
    newFields[index] = value;
    setAuthorFields(newFields);
    
    // Update form data with non-empty authors
    const authors = newFields.filter(field => field.trim() !== '');
    setFormData(prev => ({ ...prev, authors }));
    
    // Check for gaps and add error if needed
    validateAuthorFields(newFields);
    
    // Add new field if current field is filled and it's the last one
    if (value.trim() !== '' && index === newFields.length - 1) {
      setAuthorFields([...newFields, '']);
    }
  };

  const validateAuthorFields = (fields: string[]) => {
    const errors: Record<number, string> = {};
    let foundEmpty = false;
    
    for (let i = 0; i < fields.length - 1; i++) { // Exclude the last field (always empty)
      if (fields[i].trim() === '') {
        foundEmpty = true;
      } else if (foundEmpty) {
        // Found a filled field after an empty one
        for (let j = 0; j < i; j++) {
          if (fields[j].trim() === '') {
            errors[j] = 'Please fill this field before adding more authors';
          }
        }
        break;
      }
    }
    
    setAuthorErrors(errors);
  };

  const removeAuthorField = (index: number) => {
    if (authorFields.length > 1) {
      const newFields = authorFields.filter((_, i) => i !== index);
      setAuthorFields(newFields);
      
      // Update form data
      const authors = newFields.filter(field => field.trim() !== '');
      setFormData(prev => ({ ...prev, authors }));
      
      // Validate after removal
      validateAuthorFields(newFields);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate year field first
    if (!validateYear()) {
      return; // Stop submission if validation fails
    }
    
    // Get the appropriate data based on whether we're creating or updating
    const submitData = getSubmissionData();

    console.log('Submit mode:', citation ? 'UPDATE' : 'CREATE');
    console.log('Original citation type:', citation?.type);
    console.log('Current selected type:', selectedType);
    console.log('Year is None checked:', yearIsNone);
    console.log('Form year value:', formData.year);
    console.log('Calculated year value:', yearIsNone ? null : (formData.year ? parseInt(formData.year) : null));
    console.log('Submit data:', submitData);

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
    setAuthorFields(['']);
    setAuthorErrors({});
    setYearValidationError(null);
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
              className={`form-input ${
                getFieldError('title') 
                  ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                  : ''
              }`}
              required
            />
            {getFieldError('title') && (
              <p className="text-red-500 text-sm mt-1">
                {getFieldError('title')}
              </p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Authors
            </label>
            <div className="space-y-2">
              {authorFields.map((author, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div className="flex-1">
                    <input
                      type="text"
                      value={author}
                      onChange={(e) => handleAuthorChange(index, e.target.value)}
                      placeholder={
                        index === 0 
                          ? "First Author (Name Surname)" 
                          : index === 1 
                            ? "Second Author (Name Surname)"
                            : index === 2
                              ? "Third Author (Name Surname)"
                              : `Author ${index + 1} (Name Surname)`
                      }
                      className={`form-input ${
                        (authorErrors[index] || (index === 0 && getFieldError('authors')))
                          ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                          : ''
                      }`}
                    />
                    {/* Show field-specific author errors inline */}
                    {index === 0 && getFieldError('authors') && (
                      <p className="text-red-500 text-sm mt-1">
                        {getFieldError('authors')}
                      </p>
                    )}
                    {/* Show gap validation errors */}
                    {authorErrors[index] && (
                      <p className="text-red-500 text-sm mt-1">
                        {authorErrors[index]}
                      </p>
                    )}
                  </div>
                  {index < authorFields.length - 1 && authorFields.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeAuthorField(index)}
                      className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors"
                    >
                      <XMarkIcon className="h-4 w-4" />
                    </button>
                  )}
                </div>
              ))}
              {Object.keys(authorErrors).length === 0 && authorFields.length > 1 && authorFields[authorFields.length - 1] === '' && (
                <p className="text-sm text-gray-500">
                  Fill the field above to add another author
                </p>
              )}
            </div>
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
                onChange={(e) => {
                  handleInputChange('year', e.target.value);
                  // Clear validation error when user starts typing
                  if (yearValidationError) {
                    setYearValidationError(null);
                  }
                }}
                disabled={yearIsNone}
                className={`form-input disabled:bg-gray-100 ${
                  (getFieldError('year') || yearValidationError)
                    ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                    : ''
                }`}
              />
              {(getFieldError('year') || yearValidationError) && (
                <p className="text-red-500 text-sm">
                  {getFieldError('year') || yearValidationError}
                </p>
              )}
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={yearIsNone}
                  onChange={(e) => {
                    setYearIsNone(e.target.checked);
                    // Clear the year field when "Year is None" is checked
                    if (e.target.checked) {
                      handleInputChange('year', '');
                      setYearValidationError(null); // Clear validation error
                    } else {
                      // When unchecking, validate if year field is empty
                      setTimeout(() => {
                        if (!formData.year || formData.year.trim() === '') {
                          setYearValidationError('Year is required. Either enter a year or check "Year is None"');
                        }
                      }, 100);
                    }
                  }}
                  className="mr-2"
                />
                <span className="text-sm text-gray-600">Year is None</span>
              </label>
            </div>
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
                  Publisher
                </label>
                <input
                  type="text"
                  value={formData.publisher}
                  onChange={(e) => handleInputChange('publisher', e.target.value)}
                  className={`form-input ${
                    getFieldError('publisher') 
                      ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                      : ''
                  }`}
                />
                {getFieldError('publisher') && (
                  <p className="text-red-500 text-sm mt-1">
                    {getFieldError('publisher')}
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Place
                </label>
                <input
                  type="text"
                  value={formData.place}
                  onChange={(e) => handleInputChange('place', e.target.value)}
                  className={`form-input ${
                    getFieldError('place') 
                      ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                      : ''
                  }`}
                />
                {getFieldError('place') && (
                  <p className="text-red-500 text-sm mt-1">
                    {getFieldError('place')}
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Edition
                </label>
                <input
                  type="number"
                  value={formData.edition}
                  onChange={(e) => handleInputChange('edition', e.target.value)}
                  className={`form-input ${
                    getFieldError('edition') 
                      ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                      : ''
                  }`}
                />
                {getFieldError('edition') && (
                  <p className="text-red-500 text-sm mt-1">
                    {getFieldError('edition')}
                  </p>
                )}
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
                  className={`form-input ${
                    getFieldError('journal') 
                      ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                      : ''
                  }`}
                />
                {getFieldError('journal') && (
                  <p className="text-red-500 text-sm mt-1">
                    {getFieldError('journal')}
                  </p>
                )}
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
                    className={`form-input ${
                      getFieldError('volume') 
                        ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                        : ''
                    }`}
                  />
                  {getFieldError('volume') && (
                    <p className="text-red-500 text-sm mt-1">
                      {getFieldError('volume')}
                    </p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Issue
                  </label>
                  <input
                    type="text"
                    value={formData.issue}
                    onChange={(e) => handleInputChange('issue', e.target.value)}
                    className={`form-input ${
                      getFieldError('issue') 
                        ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                        : ''
                    }`}
                  />
                  {getFieldError('issue') && (
                    <p className="text-red-500 text-sm mt-1">
                      {getFieldError('issue')}
                    </p>
                  )}
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
                    className={`form-input ${
                      getFieldError('pages') 
                        ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                        : ''
                    }`}
                  />
                  {getFieldError('pages') && (
                    <p className="text-red-500 text-sm mt-1">
                      {getFieldError('pages')}
                    </p>
                  )}
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
                  className={`form-input ${
                    getFieldError('doi') 
                      ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                      : ''
                  }`}
                />
                {getFieldError('doi') && (
                  <p className="text-red-500 text-sm mt-1">
                    {getFieldError('doi')}
                  </p>
                )}
              </div>
            </>
          );
        
        case 'website':
          return (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Publisher
                </label>
                <input
                  type="text"
                  value={formData.publisher}
                  onChange={(e) => handleInputChange('publisher', e.target.value)}
                  className={`form-input ${
                    getFieldError('publisher') 
                      ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                      : ''
                  }`}
                />
                {getFieldError('publisher') && (
                  <p className="text-red-500 text-sm mt-1">
                    {getFieldError('publisher')}
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  URL
                </label>
                <input
                  type="url"
                  value={formData.url}
                  onChange={(e) => handleInputChange('url', e.target.value)}
                  className={`form-input ${
                    getFieldError('url') 
                      ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                      : ''
                  }`}
                />
                {getFieldError('url') && (
                  <p className="text-red-500 text-sm mt-1">
                    {getFieldError('url')}
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Access Date
                </label>
                <input
                  type="date"
                  value={formData.access_date}
                  onChange={(e) => handleInputChange('access_date', e.target.value)}
                  className={`form-input ${
                    getFieldError('access_date') 
                      ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                      : ''
                  }`}
                />
                {getFieldError('access_date') && (
                  <p className="text-red-500 text-sm mt-1">
                    {getFieldError('access_date')}
                  </p>
                )}
              </div>
            </div>
          );
        
        case 'report':
          return (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Publisher
                </label>
                <input
                  type="text"
                  value={formData.publisher}
                  onChange={(e) => handleInputChange('publisher', e.target.value)}
                  className={`form-input ${
                    getFieldError('publisher') 
                      ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                      : ''
                  }`}
                />
                {getFieldError('publisher') && (
                  <p className="text-red-500 text-sm mt-1">
                    {getFieldError('publisher')}
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  URL
                </label>
                <input
                  type="url"
                  value={formData.url}
                  onChange={(e) => handleInputChange('url', e.target.value)}
                  className={`form-input ${
                    getFieldError('url') 
                      ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                      : ''
                  }`}
                />
                {getFieldError('url') && (
                  <p className="text-red-500 text-sm mt-1">
                    {getFieldError('url')}
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Place
                </label>
                <input
                  type="text"
                  value={formData.place}
                  onChange={(e) => handleInputChange('place', e.target.value)}
                  className={`form-input ${
                    getFieldError('place') 
                      ? 'border-red-500 focus:border-red-500 focus:ring-red-500' 
                      : ''
                  }`}
                />
                {getFieldError('place') && (
                  <p className="text-red-500 text-sm mt-1">
                    {getFieldError('place')}
                  </p>
                )}
              </div>
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
            disabled={isLoading || !formData.title.trim() || !!yearValidationError}
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
