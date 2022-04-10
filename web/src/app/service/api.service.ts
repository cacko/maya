import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";


@Injectable({
  providedIn: "root"
})
export class ApiService {

  private readonly API_BASE = "photos.cacko.net/maya/rest";

  page = 1;

  constructor(
    private httpClient: HttpClient
  ) {

  }


  folders(page = 1, filter: string = "", folder: string = "") {
    return this.httpClient.get(
      `https://${this.API_BASE}/folders.json`);
  }

  photos(page = 1, filter: string = "", folder: string = "") {
    this.page = Math.max(1, page);
    let url = "photos";

    if (folder) {
      url = "folder";
    }

    return this.httpClient.get(
      `https://${this.API_BASE}/${url}.json`, {
        params: {
          filter: filter,
          page
        }
      }
    );
  }
}
