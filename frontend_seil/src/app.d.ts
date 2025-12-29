// src/app.d.ts
declare global {
	namespace App {
	  interface Locals {
		user?: {
		  id: string;
		  email: string;
		  nombre: string;
		  rol: string;
		  loggedIn: boolean;
		};
	  }
	  // interface Error {}
	  // interface PageData {}
	  // interface PageState {}
	  // interface Platform {}
	}
  }
  
  export {};