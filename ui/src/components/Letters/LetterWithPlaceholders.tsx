import React, { useState, useEffect } from 'react';
import { PlaceholderDetectionResult } from '../../types';
import { PlaceholderService } from '../../services/placeholderService';
import { CompanyProfileService } from '../../services/companyProfile';
import { PlaceholderTag } from './PlaceholderTag';

interface LetterWithPlaceholdersProps {
  content: string;
  onContentUpdate?: (updatedContent: string) => void;
  readOnly?: boolean;
}

export const LetterWithPlaceholders: React.FC<LetterWithPlaceholdersProps> = ({
  content: initialContent,
  onContentUpdate,
  readOnly = false,
}) => {
  const [content, setContent] = useState(initialContent);
  const [detectionResult, setDetectionResult] = useState<PlaceholderDetectionResult | null>(null);
  const [placeholderValues, setPlaceholderValues] = useState<Record<string, string>>({});

  useEffect(() => {
    // Apply company profile on mount
    const companyProfile = CompanyProfileService.get();
    let processedContent = initialContent;
    
    if (companyProfile) {
      processedContent = CompanyProfileService.applyToLetter(initialContent, companyProfile);
    }
    
    setContent(processedContent);
    const result = PlaceholderService.detect(processedContent);
    setDetectionResult(result);
    
    // Initialize placeholder values
    const values: Record<string, string> = {};
    result.placeholders.forEach(placeholder => {
      values[placeholder.pattern] = '';
    });
    setPlaceholderValues(values);
  }, [initialContent]);

  const handlePlaceholderUpdate = (pattern: string, value: string) => {
    const newValues = { ...placeholderValues, [pattern]: value };
    setPlaceholderValues(newValues);

    // Replace placeholder in content
    const updatedContent = PlaceholderService.replace(content, { [pattern]: value });
    setContent(updatedContent);
    
    // Re-detect placeholders
    const result = PlaceholderService.detect(updatedContent);
    setDetectionResult(result);

    // Notify parent
    if (onContentUpdate) {
      onContentUpdate(updatedContent);
    }
  };

  const renderContentWithPlaceholders = () => {
    if (!detectionResult || detectionResult.placeholders.length === 0) {
      return <div className="whitespace-pre-wrap">{content}</div>;
    }

    const elements: React.ReactNode[] = [];
    let lastIndex = 0;

    detectionResult.placeholders.forEach((placeholder, index) => {
      // Add text before placeholder
      if (placeholder.startIndex > lastIndex) {
        elements.push(
          <span key={`text-${index}`}>
            {content.substring(lastIndex, placeholder.startIndex)}
          </span>
        );
      }

      // Add placeholder component
      elements.push(
        <PlaceholderTag
          key={placeholder.id}
          placeholder={placeholder}
          value={placeholderValues[placeholder.pattern]}
          onUpdate={(value) => handlePlaceholderUpdate(placeholder.pattern, value)}
          readOnly={readOnly}
        />
      );

      lastIndex = placeholder.endIndex;
    });

    // Add remaining text
    if (lastIndex < content.length) {
      elements.push(
        <span key="text-final">
          {content.substring(lastIndex)}
        </span>
      );
    }

    return <div className="whitespace-pre-wrap">{elements}</div>;
  };

  const unfilled = detectionResult?.placeholders.filter(
    p => p.required && !placeholderValues[p.pattern]
  ).length || 0;

  return (
    <div>
      {unfilled > 0 && !readOnly && (
        <div className="mb-4 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
          <p className="text-sm text-amber-800 dark:text-amber-200">
            <strong>{unfilled}</strong> required placeholder{unfilled > 1 ? 's' : ''} need{unfilled === 1 ? 's' : ''} to be filled.
          </p>
        </div>
      )}
      
      <div className="prose prose-lg dark:prose-invert max-w-none">
        {renderContentWithPlaceholders()}
      </div>
    </div>
  );
};