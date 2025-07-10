import { Placeholder, PlaceholderType, PlaceholderDetectionResult } from '../types';

// Common placeholder patterns and their metadata
const PLACEHOLDER_PATTERNS: Array<{
  regex: RegExp;
  type: PlaceholderType;
  required: boolean;
  getDisplayName: (match: string) => string;
  validation?: RegExp;
}> = [
  // Date placeholders
  {
    regex: /\[(Date|Today's Date|Current Date|Insert Date)\]/gi,
    type: 'date',
    required: true,
    getDisplayName: () => 'Date',
    validation: /^\d{1,2}\/\d{1,2}\/\d{4}$/,
  },
  // Company information
  {
    regex: /\[(Company Name|Insurance Company Name|Our Company)\]/gi,
    type: 'text',
    required: true,
    getDisplayName: () => 'Company Name',
  },
  {
    regex: /\[(Company Address|Company Street Address|Our Address)\]/gi,
    type: 'address',
    required: false,
    getDisplayName: () => 'Company Address',
  },
  {
    regex: /\[(Company Phone|Company Phone Number|Our Phone)\]/gi,
    type: 'phone',
    required: false,
    getDisplayName: () => 'Company Phone',
    validation: /^[\d\s\-\(\)]+$/,
  },
  // Agent information
  {
    regex: /\[(Agent Name|Your Agent|Agent)\]/gi,
    type: 'name',
    required: false,
    getDisplayName: () => 'Agent Name',
  },
  {
    regex: /\[(Agent Title|Agent Position)\]/gi,
    type: 'text',
    required: false,
    getDisplayName: () => 'Agent Title',
  },
  {
    regex: /\[(Agent Email|Agent E-mail)\]/gi,
    type: 'email',
    required: false,
    getDisplayName: () => 'Agent Email',
    validation: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  },
  {
    regex: /\[(Agent Phone|Agent Phone Number)\]/gi,
    type: 'phone',
    required: false,
    getDisplayName: () => 'Agent Phone',
    validation: /^[\d\s\-\(\)]+$/,
  },
  // Customer information
  {
    regex: /\[(Customer Address|Policyholder Address|Client Address)\]/gi,
    type: 'address',
    required: false,
    getDisplayName: () => 'Customer Address',
  },
  // Policy information
  {
    regex: /\[(Policy Effective Date|Effective Date|Start Date)\]/gi,
    type: 'date',
    required: false,
    getDisplayName: () => 'Policy Effective Date',
    validation: /^\d{1,2}\/\d{1,2}\/\d{4}$/,
  },
  {
    regex: /\[(Policy Expiration Date|Expiration Date|End Date)\]/gi,
    type: 'date',
    required: false,
    getDisplayName: () => 'Policy Expiration Date',
    validation: /^\d{1,2}\/\d{1,2}\/\d{4}$/,
  },
  // Financial placeholders
  {
    regex: /\[(Premium Amount|Monthly Premium|Annual Premium)\]/gi,
    type: 'currency',
    required: false,
    getDisplayName: () => 'Premium Amount',
    validation: /^\$?[\d,]+(\.\d{2})?$/,
  },
  {
    regex: /\[(Coverage Amount|Policy Limit|Coverage Limit)\]/gi,
    type: 'currency',
    required: false,
    getDisplayName: () => 'Coverage Amount',
    validation: /^\$?[\d,]+(\.\d{2})?$/,
  },
  {
    regex: /\[(Deductible|Deductible Amount)\]/gi,
    type: 'currency',
    required: false,
    getDisplayName: () => 'Deductible',
    validation: /^\$?[\d,]+(\.\d{2})?$/,
  },
  {
    regex: /\[(Claim Amount|Loss Amount|Damage Amount)\]/gi,
    type: 'currency',
    required: false,
    getDisplayName: () => 'Claim Amount',
    validation: /^\$?[\d,]+(\.\d{2})?$/,
  },
  // Generic placeholder - catch all remaining [...] patterns
  {
    regex: /\[([^\]]+)\]/g,
    type: 'text',
    required: false,
    getDisplayName: (match: string) => match.slice(1, -1),
  },
];

export class PlaceholderService {
  // Detect all placeholders in the content
  static detect(content: string): PlaceholderDetectionResult {
    const placeholders: Placeholder[] = [];
    const processedRanges: Array<[number, number]> = [];

    // Check each pattern
    PLACEHOLDER_PATTERNS.forEach((pattern) => {
      const regex = new RegExp(pattern.regex.source, pattern.regex.flags);
      let match;

      while ((match = regex.exec(content)) !== null) {
        const startIndex = match.index;
        const endIndex = match.index + match[0].length;

        // Skip if this range was already processed by a more specific pattern
        const isOverlapping = processedRanges.some(
          ([start, end]) => 
            (startIndex >= start && startIndex < end) ||
            (endIndex > start && endIndex <= end)
        );

        if (!isOverlapping) {
          processedRanges.push([startIndex, endIndex]);
          
          placeholders.push({
            id: `placeholder_${startIndex}_${endIndex}`,
            pattern: match[0],
            type: pattern.type,
            required: pattern.required,
            displayName: pattern.getDisplayName(match[0]),
            validation: pattern.validation,
            startIndex,
            endIndex,
          });
        }
      }
    });

    // Sort by position in document
    placeholders.sort((a, b) => a.startIndex - b.startIndex);

    // Check if any required placeholders are unfilled
    const hasUnfilledRequired = placeholders.some(p => p.required && !p.value);

    return {
      content,
      placeholders,
      hasUnfilledRequired,
    };
  }

  // Replace placeholders with values
  static replace(content: string, values: Record<string, string>): string {
    let updatedContent = content;

    // Replace each placeholder pattern with its value
    Object.entries(values).forEach(([placeholder, value]) => {
      if (value) {
        // Escape special regex characters in the placeholder
        const escapedPlaceholder = placeholder.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        updatedContent = updatedContent.replace(new RegExp(escapedPlaceholder, 'g'), value);
      }
    });

    return updatedContent;
  }

  // Validate a placeholder value
  static validate(placeholder: Placeholder, value: string): boolean {
    if (!value && placeholder.required) {
      return false;
    }

    if (value && placeholder.validation) {
      return placeholder.validation.test(value);
    }

    return true;
  }

  // Format value based on placeholder type
  static formatValue(type: PlaceholderType, value: string): string {
    switch (type) {
      case 'date':
        // Ensure consistent date format
        if (value === 'today' || value === 'now') {
          return new Date().toLocaleDateString('en-US');
        }
        return value;

      case 'currency':
        // Ensure currency format
        const numValue = value.replace(/[^0-9.-]+/g, '');
        const num = parseFloat(numValue);
        if (!isNaN(num)) {
          return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
          }).format(num);
        }
        return value;

      case 'phone':
        // Format phone number
        const digits = value.replace(/\D/g, '');
        if (digits.length === 10) {
          return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
        }
        return value;

      default:
        return value;
    }
  }

  // Get suggested value based on placeholder type and context
  static getSuggestedValue(placeholder: Placeholder): string {
    switch (placeholder.displayName) {
      case 'Date':
      case 'Today\'s Date':
      case 'Current Date':
        return new Date().toLocaleDateString('en-US');
      
      case 'Agent Title':
        return 'Insurance Agent';
      
      default:
        return '';
    }
  }

  // Extract all unique placeholder patterns from content
  static extractPatterns(content: string): string[] {
    const patterns = new Set<string>();
    const regex = /\[([^\]]+)\]/g;
    let match;

    while ((match = regex.exec(content)) !== null) {
      patterns.add(match[0]);
    }

    return Array.from(patterns);
  }
}