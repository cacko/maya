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

  private readonly API_BASE = "https://photos.cacko.net/maya/rest";

  constructor(
    private httpClient: HttpClient
  ) {

  }

  load(page = 1) {
    this.httpClient.get(`${this.API_BASE}/photos.json`, {
      params: {per_page: 100, page}
    }).subscribe({
      next: (data) => {
        const items = data as PhotoEntity[];
        this.photosSubject.next(items);
      }, error: (err) => {
        console.error(err);
      }
    });
  }
}
