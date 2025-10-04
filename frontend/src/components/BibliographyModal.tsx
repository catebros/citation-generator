import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ClipboardDocumentIcon, CheckIcon } from '@heroicons/react/24/outline';
import DOMPurify from 'dompurify';
import Modal from './Modal';
import LoadingSpinner from './LoadingSpinner';
import type { BibliographyResponse } from '../types';

interface BibliographyModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: number;
  onGenerate: (projectId: number, formatType: 'apa' | 'mla') => Promise<BibliographyResponse>;
}

interface BibliographyItemProps {
  text: string;
}

const BibliographyItem: React.FC<BibliographyItemProps> = ({ text }) => {
  return (
    <p
      className="text-sm leading-relaxed mb-4 last:mb-0"
      dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(text) }}
    />
  );
};

const BibliographyModal: React.FC<BibliographyModalProps> = ({
  isOpen,
  onClose,
  projectId,
  onGenerate,
}) => {
  const [selectedFormat, setSelectedFormat] = useState<'apa' | 'mla' | null>(null);
  const [bibliography, setBibliography] = useState<BibliographyResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isCopied, setIsCopied] = useState(false);

  const handleFormatSelect = async (format: 'apa' | 'mla') => {
    if (isLoading) return; // Prevent multiple clicks during loading
    
    try {
      setIsLoading(true);
      setSelectedFormat(format);
      const result = await onGenerate(projectId, format);
      setBibliography(result);
    } catch (err) {
      // Error handling is done in the hook
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyAll = async () => {
    if (!bibliography?.bibliography) return;

    // Keep HTML formatting for italics instead of converting to plain text
    const htmlBibliography = bibliography.bibliography.map(item => 
      DOMPurify.sanitize(item)
    ).join('\n\n');

    try {
      // Try to copy as HTML first, fallback to plain text
      if (navigator.clipboard && window.ClipboardItem) {
        const htmlBlob = new Blob([htmlBibliography], { type: 'text/html' });
        const textBlob = new Blob([htmlBibliography.replace(/<\/?[^>]+(>|$)/g, "")], { type: 'text/plain' });
        const item = new ClipboardItem({
          'text/html': htmlBlob,
          'text/plain': textBlob
        });
        await navigator.clipboard.write([item]);
      } else {
        // Fallback for older browsers
        await navigator.clipboard.writeText(htmlBibliography.replace(/<\/?[^>]+(>|$)/g, ""));
      }
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  const handleClose = () => {
    setSelectedFormat(null);
    setBibliography(null);
    setIsLoading(false);
    setIsCopied(false);
    onClose();
  };

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={handleClose} 
      title="Generate Bibliography"
      size="xl"
    >
      <div className="space-y-6">
        {/* Format Selection */}
        {!bibliography && (
          <div>
            <h4 className="text-lg font-medium text-gray-900 mb-4">
              Choose Citation Format
            </h4>
            <div className="grid grid-cols-2 gap-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleFormatSelect('apa')}
                className={`
                  p-6 rounded-lg border-2 transition-all duration-200 text-left
                  ${selectedFormat === 'apa'
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
                  }
                  ${isLoading ? 'opacity-50' : ''}
                `}
              >
                <div className="font-semibold text-lg text-gray-900 mb-2">APA Style</div>
                <div className="text-sm text-gray-600">
                  American Psychological Association (7th edition)
                  <br />
                  <span className="italic">Author, A. A. (Year). Title of work.</span>
                </div>
                {isLoading && selectedFormat === 'apa' && (
                  <div className="mt-3">
                    <LoadingSpinner size="sm" />
                  </div>
                )}
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleFormatSelect('mla')}
                className={`
                  p-6 rounded-lg border-2 transition-all duration-200 text-left
                  ${selectedFormat === 'mla'
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
                  }
                  ${isLoading ? 'opacity-50' : ''}
                `}
              >
                <div className="font-semibold text-lg text-gray-900 mb-2">MLA Style</div>
                <div className="text-sm text-gray-600">
                  Modern Language Association (9th edition)
                  <br />
                  <span className="italic">Author, First. "Title of Work." Publication.</span>
                </div>
                {isLoading && selectedFormat === 'mla' && (
                  <div className="mt-3">
                    <LoadingSpinner size="sm" />
                  </div>
                )}
              </motion.button>
            </div>
          </div>
        )}

        {/* Bibliography Display */}
        {bibliography && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-medium text-gray-900">
                {bibliography.format_type.toUpperCase()} Bibliography
              </h4>
              
              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    setBibliography(null);
                    setSelectedFormat(null);
                  }}
                  className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  Change Format
                </button>
                
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleCopyAll}
                  className="px-3 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 flex items-center space-x-2"
                >
                  {isCopied ? (
                    <>
                      <CheckIcon className="h-4 w-4" />
                      <span>Copied!</span>
                    </>
                  ) : (
                    <>
                      <ClipboardDocumentIcon className="h-4 w-4" />
                      <span>Copy All</span>
                    </>
                  )}
                </motion.button>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-6 max-h-96 overflow-y-auto">
              {bibliography.bibliography.length > 0 ? (
                bibliography.bibliography.map((citation, index) => (
                  <BibliographyItem key={index} text={citation} />
                ))
              ) : (
                <p className="text-gray-500 text-center py-8">
                  No citations available to generate bibliography.
                </p>
              )}
            </div>
            
            <div className="mt-4 text-xs text-gray-500">
              {bibliography.bibliography.length} citation{bibliography.bibliography.length !== 1 ? 's' : ''} found
            </div>
          </div>
        )}

        {/* Close Button */}
        <div className="flex justify-end pt-4 border-t">
          <button
            onClick={handleClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            Close
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default BibliographyModal;