import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { getGitHubRepositoryUrl, isGitHubPages } from "../../config/environment";

interface InterviewCtaProps {
  children: ReactNode;
  className?: string;
}

export function InterviewCta({ children, className }: InterviewCtaProps) {
  if (isGitHubPages()) {
    return (
      <a
        className={className}
        href={getGitHubRepositoryUrl()}
        target="_blank"
        rel="noopener noreferrer"
      >
        {children}
      </a>
    );
  }

  return (
    <Link className={className} to="/interview">
      {children}
    </Link>
  );
}
