const DEFAULT_GITHUB_REPOSITORY_URL = "https://github.com/JuanjoLopez19/job-offer-talk";

export function isGitHubPages(): boolean {
  return import.meta.env.VITE_GITHUB_PAGES === "true";
}

export function getGitHubRepositoryUrl(): string {
  return import.meta.env.VITE_GITHUB_REPOSITORY_URL || DEFAULT_GITHUB_REPOSITORY_URL;
}
