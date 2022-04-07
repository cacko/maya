import { Injectable } from "@angular/core";
import { Subject } from "rxjs";
import { PhotoEntity } from "../entity/photo";
import { HttpClient } from "@angular/common/http";

@Injectable({
  providedIn: "root"
})
export class PhotosService {

  private photosSubject = new Subject<PhotoEntity[]>();
  photos = this.photosSubject.asObservable();

  private photoSubject = new Subject<string | null>();
  photo = this.photoSubject.asObservable();

  private readonly API_BASE = "https://photos.cacko.net/maya/rest";

  page = 1;

  constructor(
    private httpClient: HttpClient
  ) {

  }

  load(page = 1) {
    this.page = page;
    this.httpClient.get(`${this.API_BASE}/photos/${page}`).subscribe({
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
