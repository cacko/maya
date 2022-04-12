import {Injectable} from "@angular/core";
import {HttpClient} from "@angular/common/http";


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

  photos(page = 1, filter: string = "", folder: string = "", face: string = "") {
    this.page = Math.max(1, page);
    let path = "photos.json";

    if (face.length) {
      path = `face/${face}`;
    }
    return this.httpClient.get(
      `https://${this.API_BASE}/${path}`, {
        params: {
          filter,
          folder,
          page
        }
      }
    );
  }
}
