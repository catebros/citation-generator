// utils/errorParser.ts

export interface FieldError {
  field: string;
  message: string;
  type: 'format' | 'missing';
}

export interface ParsedErrors {
  fieldErrors: Record<string, string>; // field -> error message for inline display
  generalError: string | null; // for missing fields or other general errors
}

/**
 * Parse error message from backend and categorize as field-specific format errors
 * or general errors (like missing fields)
 */
export function parseValidationError(errorMessage: string): ParsedErrors {
  const result: ParsedErrors = {
    fieldErrors: {},
    generalError: null
  };

  // Check for missing fields error
  if (errorMessage.includes('Missing required') && errorMessage.includes('fields:')) {
    result.generalError = errorMessage;
    return result;
  }

  // Check for invalid fields error
  if (errorMessage.includes('Invalid fields for') || errorMessage.includes('Type change from')) {
    result.generalError = errorMessage;
    return result;
  }

  // Check for specific field format errors
  const fieldFormatPatterns = [
    // URL errors
    { pattern: /Invalid URL format/i, field: 'url' },
    
    // DOI errors  
    { pattern: /Invalid DOI format/i, field: 'doi' },
    
    // Pages errors
    { pattern: /Pages must be in format/i, field: 'pages' },
    
    // Access Date errors
    { pattern: /Access Date must be in YYYY-MM-DD format/i, field: 'access_date' },
    
    // Year errors
    { pattern: /Year must be a non-negative integer/i, field: 'year' },
    { pattern: /Year must be an integer or null/i, field: 'year' },
    
    // Volume errors
    { pattern: /Volume must be a positive integer/i, field: 'volume' },
    
    // Edition errors
    { pattern: /Edition must be a positive integer/i, field: 'edition' },
    
    // String field errors
    { pattern: /Title must be a non-empty string/i, field: 'title' },
    { pattern: /Publisher must be a non-empty string/i, field: 'publisher' },
    { pattern: /Place must be a non-empty string/i, field: 'place' },
    { pattern: /Journal must be a non-empty string/i, field: 'journal' },
    { pattern: /Issue must be a non-empty string/i, field: 'issue' },
    
    // Authors errors
    { pattern: /Authors must be a list/i, field: 'authors' },
    { pattern: /Authors list cannot be empty/i, field: 'authors' },
    { pattern: /All authors must be non-empty strings/i, field: 'authors' },
    { pattern: /Author names can only contain letters, spaces, hyphens, apostrophes, and periods/i, field: 'authors' },
    
    // Place errors
    { pattern: /Place names can only contain letters, spaces, hyphens, apostrophes, periods, and commas/i, field: 'place' },
  ];

  // Try to match field-specific format errors
  for (const { pattern, field } of fieldFormatPatterns) {
    if (pattern.test(errorMessage)) {
      result.fieldErrors[field] = errorMessage;
      return result;
    }
  }

  // If no specific field error matched, treat as general error
  result.generalError = errorMessage;
  return result;
}

/**
 * Get user-friendly error messages for inline display
 */
export function getInlineErrorMessage(field: string, originalMessage: string): string {
  const friendlyMessages: Record<string, Record<string, string>> = {
    url: {
      'Invalid URL format': 'Please enter a valid URL (e.g., https://example.com)',
      'URL must be a string': 'URL must be text'
    },
    doi: {
      'Invalid DOI format (expected: 10.xxxx/xxxx)': 'Please enter a valid DOI (e.g., 10.1234/example.doi)',
      'DOI must be a string': 'DOI must be text'
    },
    pages: {
      'Pages must be in format \'start-end\' or multiple ranges like \'1-3, 5-7\' (e.g., \'123-145\' or \'1-3, 5-7\')': 'Use format like "123-145" or "1-3, 5-7"',
      'Pages must be a string': 'Pages must be text'
    },
    access_date: {
      'Access Date must be in YYYY-MM-DD format': 'Please use YYYY-MM-DD format',
      'Access Date must be a string': 'Access date must be text'
    },
    year: {
      'Year must be an integer or null': 'Please enter a valid year or check "Year is None"',
      'Year must be a non-negative integer not exceeding': 'Please enter a valid year'
    },
    volume: {
      'Volume must be a positive integer': 'Please enter a positive number'
    },
    edition: {
      'Edition must be a positive integer': 'Please enter a positive number'
    },
    title: {
      'Title must be a non-empty string': 'Title cannot be empty'
    },
    publisher: {
      'Publisher must be a non-empty string': 'Publisher cannot be empty'
    },
    place: {
      'Place must be a non-empty string': 'Place cannot be empty',
      'Place names can only contain letters, spaces, hyphens, apostrophes, periods, and commas': 'Place names cannot contain numbers or special characters'
    },
    journal: {
      'Journal must be a non-empty string': 'Journal cannot be empty'
    },
    issue: {
      'Issue must be a non-empty string': 'Issue cannot be empty'
    },
    authors: {
      'Authors must be a list': 'Authors format error',
      'Authors list cannot be empty': 'Please add at least one author',
      'All authors must be non-empty strings': 'All author names must be filled',
      'Author names can only contain letters, spaces, hyphens, apostrophes, and periods': 'Author names cannot contain numbers or special characters'
    }
  };

  const fieldMessages = friendlyMessages[field];
  if (fieldMessages) {
    // Try exact match first
    if (fieldMessages[originalMessage]) {
      return fieldMessages[originalMessage];
    }
    
    // Try partial match for messages with dynamic content (like year)
    for (const [pattern, friendlyMessage] of Object.entries(fieldMessages)) {
      if (originalMessage.includes(pattern.split(' not exceeding')[0])) {
        return friendlyMessage;
      }
    }
  }

  // Fallback to original message if no friendly version found
  return originalMessage;
}