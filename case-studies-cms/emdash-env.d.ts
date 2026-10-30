/// <reference types="emdash/locals" />
import type {PortableTextBlock} from 'emdash';
export interface CaseStudy {
 id:string; slug:string|null; status:string; title:string; client:string; summary:string;
 poster_url?:string; poster_alt?:string; video_url?:string; video_duration?:string; content?:PortableTextBlock[];
 createdAt:Date; updatedAt:Date; publishedAt:Date|null;
}
declare module 'emdash' { interface EmDashCollections { case_studies:CaseStudy; } }
