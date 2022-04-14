import {Injectable} from "@angular/core";
import {
  HttpClient,
  HttpErrorResponse,
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest
} from "@angular/common/http";
import {AuthService} from "./auth.service";
import {Observable, Subject} from "rxjs";
import {tap} from "rxjs/operators";


@Injectable({
  providedIn: "root"
})
export class ApiService implements HttpInterceptor {

  private readonly API_BASE = "photos.cacko.net/maya/rest";

  errorSubject = new Subject<string>();
  error = this.errorSubject.asObservable();

  page = 1;

  constructor(
    private httpClient: HttpClient,
    public auth: AuthService
  ) {

  }

  intercept(
    req: HttpRequest<any>,
    next: HttpHandler
  ): Observable<HttpEvent<any>> {
    const headers = req.headers.set("token", this.auth.token);
    return next.handle(req.clone({headers}
    )).pipe(
      tap(
        (event: HttpEvent<any>) => {
        },
        (err: HttpErrorResponse) => {
          this.errorSubject.next(err.message);
        }
      )
    );
  }


  folders(page = 1, filter: string = "", folder: string = "") {
    return this.httpClient.get(
      `https://${this.API_BASE}/folders.json`);
  }

  faces() {
    return this.httpClient.get(
      `https://${this.API_BASE}/faces.json`);
  }

  photos(page = 1, filter: string = "", folder: string = "", face: string = "") {
    this.page = Math.max(1, page);
    let path = "photos.json";
    return this.httpClient.get(
      `https://${this.API_BASE}/${path}`, {
        params: {
          filter,
          folder,
          page,
          face
        }
      }
    );
  }
}
