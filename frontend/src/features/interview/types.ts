export type ChatMessage = {
  id: string;
  role: "assistant" | "user";
  content: string;
};

export type GraphResponse = {
  assistant_message: string;
  conditional_edge?: string | null;
  is_tts_message?: boolean;
  node_name?: string;
  session_id?: string;
  job_offer_context?: JobOfferContext | null;
  job_offer_generated_info?: JobOfferGeneratedInfo | null;
};

export type JobOfferContext = {
  title: string | null;
  company_name: string | null;
  url: string;
};

export type JobOfferGeneratedInfo = {
  summary: string;
  keywords: string[];
};
