import { Injectable } from "@angular/core";
import { Subject } from "rxjs";
import { PhotoEntity } from "../entity/photo";
import { HttpClient } from "@angular/common/http";
import { environment } from "../../environments/environment";


@Injectable({
  providedIn: "root"
})
export class PhotosService {

  private photosSubject = new Subject<PhotoEntity[]>();
  photos = this.photosSubject.asObservable();

  private photoSubject = new Subject<string | null>();
  photo = this.photoSubject.asObservable();

  private readonly API_BASE = "photos.cacko.net/maya/rest";

  page = 1;

  constructor(
    private httpClient: HttpClient
  ) {

  }

  load(page = 1, query: string = "") {
    this.page = Math.max(1, page);
    const scheme = environment.production ? "https:" : "https:";
    if (query.length > 0) {
      query = encodeURIComponent(query);
      query = "/" + query;
    }
    this.httpClient.get(`${scheme}//${this.API_BASE}/photos/${this.page}${query}.json`).subscribe({
      next: (data) => {
        const items = data as PhotoEntity[];
        this.photosSubject.next(items);
      }, error: (err) => {
        throw err;
      }
    });
  }


  expand(id?: string) {
    id && this.photoSubject.next(id);
  }

  shrink() {
    this.photoSubject.next(null);
  }
}
