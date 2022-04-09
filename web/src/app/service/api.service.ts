import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { environment } from "../../environments/environment";


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

  load(page = 1, filter: string = "", folder: string = "") {
    this.page = Math.max(1, page);
    const scheme = environment.production ? "https:" : "https:";

    let url = "photos";

    if (folder) {
      url = "folder";
    }

    return this.httpClient.get(
      `${scheme}//${this.API_BASE}/${url}.json`, {
        params: {
          filter:filter,
          page
        }
      }
    )
  }
}
