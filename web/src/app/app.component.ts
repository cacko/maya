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
import { SwUpdate, VersionReadyEvent } from "@angular/service-worker";
import { MatSnackBar } from "@angular/material/snack-bar";
import { filter, map, Subscription, timer } from "rxjs";
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
  updating = true;
  selected: string | undefined | null = null;
  loading = true;
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
      swUpdate.versionUpdates.pipe(
        filter((evt): evt is VersionReadyEvent => evt.type === "VERSION_READY"),
        map(evt => ({
          type: "UPDATE_AVAILABLE",
          current: evt.currentVersion,
          available: evt.latestVersion
        }))).subscribe((res) => {
        console.log("update available", res);
        this.swUpdate
          .activateUpdate()
          .then(() => document.location.reload());
      });
    }
    this.auth.isLogged.subscribe(res => {
      if (res) {
        this.loading = true;
        this.imageService.load().then(() => {
          this.loading = false;
        });
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
    this.imageService.loading.subscribe(val => {
      setTimeout(() => {
        this.loading = !!val;
      }, 0);
    });
    this.imageService.selected.subscribe((selected) => {
      console.log(`selected=${selected}`);
      const oldId = this.selected;
      this.selected = selected;
      this.isHorizontal = !!selected;
      if (selected) {
        this.router.navigate(["photo", selected]).then(() => {
          console.log(`loaded ${selected}`);
        });
      } else {
        this.router.navigate([""]).then(() => {
          console.log(`loaded ${selected}`);
          if (oldId) {
            (async () => {
              this.imageService.endLoader();
              await this.imageService.unselect();
              this.viewportScroller.scrollToAnchor(oldId);
            })();
          }
        });
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
  };

  async ngOnInit() {
    this.route.params.subscribe((params) => {
      const filter = params["filter"];
      filter && setTimeout(() => {
        this.query = filter;
        this.keywords = this.query.split(" ");
        this.imageService.setFilter(filter);
        this.imageService.load();
        this.keywords = this.query.split(" ");
        this.imageService.endLoader();
      });
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
        this.doSearch(this.query);
      });

      return false;
    });

  }

  async doSearch(filter: string) {
    if (filter.length) {
      await this.router.navigate(["_", filter]);
    } else {
      await this.router.navigate([""]);
    }
  }

  openWithTemplate(tpl: TemplateRef<any> | undefined) {
    tpl && this.overlayRef?.attach(new TemplatePortal(tpl, this.viewContainerRef));
  }

  async onScrollDown() {
    await this.imageService.load();
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
      this.imageService.unselect();
    }
  }

  showSearch(originator: SearchOriginator) {
    if (originator == SearchOriginator.BUTTON && this.query.length > 0) {
      this.resetSearch();
      return;
    }
    setTimeout(() => {
      this.openWithTemplate(this.tpl);
      this.searchInput?.nativeElement.focus();
      this.isSearching = true;
    }, 0);
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
    this.imageService.startLoader();
    this.imageService.load().then(() => {
      this.imageService.endLoader();
    });
  }

  onSearch() {
    return this.isSearching
      ? this.hideSearch(SearchOriginator.BUTTON)
      : this.showSearch(SearchOriginator.BUTTON);
  }

  async removeKeyword(word: string) {
    this.keywords = this.keywords.filter(a => a != word);
    this.query = this.keywords.join(" ");
    await this.doSearch(this.query);
  }

}
