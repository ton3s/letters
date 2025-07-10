import React, { useState, useRef, useEffect } from 'react';
import { Placeholder } from '../../types';
import { PlaceholderService } from '../../services/placeholderService';
import { CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';

interface PlaceholderTagProps {
  placeholder: Placeholder;
  value?: string;
  onUpdate: (value: string) => void;
  readOnly?: boolean;
}

export const PlaceholderTag: React.FC<PlaceholderTagProps> = ({
  placeholder,
  value = '',
  onUpdate,
  readOnly = false,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(value);
  const [isValid, setIsValid] = useState(true);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleClick = () => {
    if (!readOnly && !isEditing) {
      setIsEditing(true);
      setEditValue(value);
    }
  };

  const handleSave = () => {
    const formattedValue = PlaceholderService.formatValue(placeholder.type, editValue);
    const valid = PlaceholderService.validate(placeholder, formattedValue);
    
    if (valid) {
      onUpdate(formattedValue);
      setIsEditing(false);
      setIsValid(true);
    } else {
      setIsValid(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditValue(value);
    setIsValid(true);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  const getSuggestedValue = () => {
    const suggested = PlaceholderService.getSuggestedValue(placeholder);
    if (suggested) {
      setEditValue(suggested);
    }
  };

  const isFilled = !!value;
  const isRequired = placeholder.required;

  if (isEditing) {
    return (
      <span className="inline-flex items-center">
        <input
          ref={inputRef}
          type={placeholder.type === 'email' ? 'email' : 'text'}
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onBlur={handleSave}
          onKeyDown={handleKeyDown}
          className={`px-2 py-1 text-sm border rounded focus:outline-none focus:ring-2 focus:ring-primary-500 ${
            !isValid ? 'border-red-500 bg-red-50' : 'border-gray-300'
          }`}
          placeholder={placeholder.displayName}
        />
        {PlaceholderService.getSuggestedValue(placeholder) && (
          <button
            onClick={getSuggestedValue}
            className="ml-1 text-xs text-primary-600 hover:text-primary-700"
            title="Use suggested value"
          >
            Auto
          </button>
        )}
      </span>
    );
  }

  return (
    <span
      onClick={handleClick}
      className={`inline-flex items-center px-2 py-1 rounded text-sm font-medium cursor-pointer transition-colors ${
        isFilled
          ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
          : isRequired
          ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400 border-b-2 border-dashed border-amber-400'
          : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 border-b-2 border-dashed border-gray-400'
      } ${!readOnly && 'hover:opacity-80'}`}
      title={`${placeholder.displayName}${isRequired ? ' (Required)' : ''}${!readOnly ? ' - Click to edit' : ''}`}
    >
      {isFilled ? (
        <>
          <CheckCircleIcon className="w-4 h-4 mr-1" />
          {value}
        </>
      ) : (
        <>
          {isRequired && <ExclamationCircleIcon className="w-4 h-4 mr-1" />}
          {placeholder.pattern}
        </>
      )}
    </span>
  );
};