export interface CompanyProfile {
  companyName: string;
  companyAddress: string;
  companyPhone: string;
  companyEmail: string;
  companyWebsite: string;
  logoUrl?: string;
  defaultAgentName?: string;
  defaultAgentTitle?: string;
  defaultAgentEmail?: string;
  defaultAgentPhone?: string;
  letterheadText?: string;
  footerText?: string;
  disclaimerText?: string;
}

const STORAGE_KEY = 'company_profile';

export class CompanyProfileService {
  // Get the company profile from localStorage
  static get(): CompanyProfile | null {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      console.error('Error reading company profile:', error);
      return null;
    }
  }

  // Save the company profile to localStorage
  static save(profile: CompanyProfile): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
    } catch (error) {
      console.error('Error saving company profile:', error);
    }
  }

  // Update specific fields in the company profile
  static update(updates: Partial<CompanyProfile>): void {
    const current = this.get() || {} as CompanyProfile;
    const updated = { ...current, ...updates };
    this.save(updated);
  }

  // Clear the company profile
  static clear(): void {
    localStorage.removeItem(STORAGE_KEY);
  }

  // Get default profile for new users
  static getDefault(): CompanyProfile {
    return {
      companyName: 'Insurance Company',
      companyAddress: '123 Main Street, Anytown, ST 12345',
      companyPhone: '(555) 123-4567',
      companyEmail: 'info@insurancecompany.com',
      companyWebsite: 'www.insurancecompany.com',
      logoUrl: '',
      defaultAgentName: '',
      defaultAgentTitle: 'Insurance Agent',
      defaultAgentEmail: '',
      defaultAgentPhone: '',
      letterheadText: '[Insurance Company Letterhead]',
      footerText: '',
      disclaimerText: 'This letter is for informational purposes only and does not constitute a contract or agreement.',
    };
  }

  // Apply company profile to letter content
  static applyToLetter(letterContent: string, profile?: CompanyProfile): string {
    const companyProfile = profile || this.get();
    
    let updatedContent = letterContent;
    
    // Replace [Date] with current date
    const currentDate = new Date().toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
    updatedContent = updatedContent.replace(/\[Date\]/g, currentDate);
    
    // Only proceed with company replacements if we have a profile
    if (!companyProfile) return updatedContent;

    // Replace common placeholders - include variations
    const replacements: Record<string, string> = {
      '[Insurance Company Letterhead]': companyProfile.letterheadText || companyProfile.companyName,
      '[Insurance Company Name]': companyProfile.companyName,
      '[Company Name]': companyProfile.companyName,
      '[Company Address]': companyProfile.companyAddress,
      '[Company Phone]': companyProfile.companyPhone,
      '[Company Email]': companyProfile.companyEmail,
      '[Company Website]': companyProfile.companyWebsite,
      '[website URL]': companyProfile.companyWebsite,
      '[Agent Name]': companyProfile.defaultAgentName || '[Agent Name]',
      '[Agent Title]': companyProfile.defaultAgentTitle || '[Agent Title]',
      '[Agent Email]': companyProfile.defaultAgentEmail || '[Agent Email]',
      '[Agent Phone]': companyProfile.defaultAgentPhone || '[Agent Phone]',
    };

    // Replace all placeholders
    Object.entries(replacements).forEach(([placeholder, value]) => {
      if (value && value !== placeholder) {
        updatedContent = updatedContent.replace(new RegExp(escapeRegExp(placeholder), 'g'), value);
      }
    });

    return updatedContent;
  }
}

// Helper function to escape special regex characters
function escapeRegExp(string: string): string {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}