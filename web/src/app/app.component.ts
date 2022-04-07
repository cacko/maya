import {
  AfterViewInit,
  Component,
  ElementRef,
  HostListener,
  OnInit,
  TemplateRef,
  ViewChild,
  ViewContainerRef
} from "@angular/core";
import { AuthService } from "./service/auth.service";
import { PhotosService } from "./service/photos.service";
import { SwUpdate } from "@angular/service-worker";
import { MatSnackBar } from "@angular/material/snack-bar";
import { interval, Subscription, timer } from "rxjs";
import { ImageService } from "./service/image.service";
import { ActivatedRoute, Router } from "@angular/router";
import { ViewportScroller } from "@angular/common";
import { FormBuilder, FormControl, FormGroup } from "@angular/forms";
import { Overlay, OverlayConfig, OverlayRef } from "@angular/cdk/overlay";
import { TemplatePortal } from "@angular/cdk/portal";


enum SearchOriginator {
  BUTTON = 1,
  ESC = 2,
  ENTER = 3,
  SLASH = 4,
  INIT = 5,
  BACKDROP = 6,
}

const SEARCH_STATES = ["search", "search_off"];


@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"]
})
export class AppComponent implements OnInit, AfterViewInit {
  title = "app";
  page = 1;
  loading: boolean = true;
  updating = true;
  selected: string | undefined | null = null;

  throttle = 50;
  scrollDistance = 2;
  scrollUpDistance = 1.5;
  isHorizontal = false;
  form: FormGroup;
  query: string = "";
  isSearching = false;
  keywords: string[] = [];

  private keyboardInterval: Subscription | undefined;
  private overlayRef: OverlayRef | undefined;

  @ViewChild("search") searchInput: ElementRef | undefined;
  @ViewChild("searchForm") tpl: TemplateRef<any> | undefined;

  constructor(
    public auth: AuthService,
    public photos: PhotosService,
    public imageService: ImageService,
    private swUpdate: SwUpdate,
    private snackBar: MatSnackBar,
    private router: Router,
    private scroller: ViewportScroller,
    private route: ActivatedRoute,
    private viewportScroller: ViewportScroller,
    private builder: FormBuilder,
    private overlay: Overlay,
    private viewContainerRef: ViewContainerRef
  ) {
    if (this.swUpdate.isEnabled) {
      this.swUpdate.available.subscribe((evt) => {
        this.updating = true;
        this.snackBar
          .open("Update is available", "Update")
          .onAction()
          .subscribe(() =>
            this.swUpdate
              .activateUpdate()
              .then(() => document.location.reload())
          );
      });
      interval(10000).subscribe(() => {
        this.swUpdate.checkForUpdate();
      });
    }
    this.auth.isLogged.subscribe(res => {
      if (res) {
        this.photos.photos.subscribe(data => {
          this.imageService.append(data);
          this.loading = false;
        });
        this.photos.load();
      }
    });
    this.form = this.builder.group({
      query: new FormControl()
    });

    this.route.queryParams.subscribe({
      next: (params) => {
        const filter = params["filter"];
        if (!filter) {
          return;
        }
        this.keywords = filter.split(" ");
        this.form.get("query")?.patchValue(filter);
      }
    });
  }

  ngAfterViewInit(): void {
    const positionStrategy = this.overlay
      .position()
      .global()
      .centerHorizontally()
      .centerVertically();
    const configs = new OverlayConfig({
      hasBackdrop: true,
      panelClass: ["search-overlay", "is-active"],
      backdropClass: "search-backdrop",
      positionStrategy
    });
    this.overlayRef = this.overlay.create(configs);
    this.overlayRef.backdropClick().subscribe(() => {
      this.hideSearch(SearchOriginator.BACKDROP);
    });
  }

  ngOnInit(): void {
    this.selected = null;
    this.route.params.subscribe((params) => {
      const id = params["id"];
      const page = params["page"];
      const filter = params["filter"];
      id && setTimeout(() => {
        this.imageService.endLoader();
        this.viewportScroller.scrollToAnchor(id);
      }, 0);
      page && filter && setTimeout(() => {
        this.query = filter;
        this.keywords = this.query.split(" ");
        this.imageService.clear();
        this.photos.load(1, this.query);
        this.keywords = this.query.split(" ");
      });
    });
    this.photos.photo.subscribe((selected) => {
      setTimeout(() => {
        const oldId = this.selected;
        this.selected = selected;
        this.isHorizontal = !!selected;
      }, 0);
    });
    this.imageService.loading.subscribe(val => {
      setTimeout(() => {
        this.loading = !!val;
      }, 0);
    });
    this.form.get("query")?.valueChanges.subscribe((value: string) => {
      if (this.keyboardInterval && !this.keyboardInterval.closed) {
        this.keyboardInterval.unsubscribe();
      }

      this.query = value?.trim().toLowerCase() || "";

      this.keyboardInterval = timer(1000).subscribe(() => {
        if (this.query.length > 0 && this.query.length < 3) {
          return;
        }
        this.doSearch(1, this.query);
      });

      return false;
    });


    // if ("filter" in this.route.snapshot.queryParams) {
    //   this.form
    //     .get("query")
    //     ?.patchValue(this.route.snapshot.queryParams.filter);
    //   this.api.searchSubject.next(true);
    // }
  }


  doSearch(page: number, filter: string) {
    this.router.navigate(["_", page, filter]);
  }


  openWithTemplate(tpl: TemplateRef<any> | undefined) {
    tpl && this.overlayRef?.attach(new TemplatePortal(tpl, this.viewContainerRef));
  }

  onScrollDown() {
    this.photos.load(++this.page);
  }


  @HostListener("document:keydown.enter", ["$event"])
  onEnter() {
    if (!this.isSearching) {
      return;
    }
    this.hideSearch(SearchOriginator.ENTER);
  }

  @HostListener("document:keydown.escape", ["$event"])
  onEscape() {
    if (this.selected) {
      this.photos.shrink();
    }
  }


  showSearch(originator: SearchOriginator) {
    if (originator == SearchOriginator.BUTTON && this.query.length > 0) {
      this.resetSearch();
      return;
    }
    this.openWithTemplate(this.tpl);
    setTimeout(() => {
      this.searchInput?.nativeElement.focus();
    });
    this.isSearching = true;
  }

  hideSearch(originator: SearchOriginator) {
    this.isSearching = false;
    this.overlayRef?.detach();
  }

  get searchIcon(): string {
    return SEARCH_STATES[+(this.isSearching || this.query?.trim().length > 0)];
  }

  resetSearch() {
    this.form.get("query")?.reset();
    this.imageService.clear();
    this.photos.load();
  }

  onSearch() {
    return this.isSearching
      ? this.hideSearch(SearchOriginator.BUTTON)
      : this.showSearch(SearchOriginator.BUTTON);
  }

  removeKeyword(word: string) {

  }

}
