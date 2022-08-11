set nocompatible
syntax enable
filetype plugin indent on
" Number of spaces per tab key
set tabstop=2
set shiftwidth=2
" inserts as many tabs for indents, then the remainder spaces
" set softtabstop=2
" All tabs converted to spaces
set expandtab
set autoindent
autocmd FileType make setlocal noexpandtab autoindent
autocmd FileType c setlocal tabstop=4 shiftwidth=4 expandtab  autoindent
autocmd FileType cpp setlocal tabstop=4 shiftwidth=4 expandtab autoindent
autocmd FileType python setlocal tabstop=2 shiftwidth=2 expandtab autoindent
au bufRead,BufNewFile *.gpl set filetype=gpl
autocmd FileType gpl setlocal tabstop=4 shiftwidth=4 expandtab autoindent
autocmd FileType l setlocal tabstop=4 shiftwidth=4 expandtab autoindent
autocmd FileType y setlocal tabstop=4 shiftwidth=4 expandtab autoindent
set number
set showcmd
set showmatch
set incsearch
set hlsearch
set foldenable
set foldlevelstart=10
set foldnestmax=10
inoremap jj <esc>

"Highlight color
highlight Search ctermbg=Gray
highlight Visual ctermbg=Gray


"spelling
"z= suggestions
" :set nospell to turn off
"set spell spelllang=en_us

set scrolloff=3
set mouse=a

" Search down recursively into all subfolders and display all matching files when we tab complete
set path+=**
set wildmenu

" Disable beep noise
set visualbell

" Disable screen flash
set belloff=all

" FILE BROWSING:
" - :edit a folder to open a file browser
" - <CR>/v/t to open in an h-split/v-split/tab
" - check |netrw-browse-maps| for more mappings
let g:netrw_banner=0        " disable annoying banner
let g:netrw_browse_split=4  " open in prior window
let g:netrw_altv=1          " open splits to the right
let g:netrw_liststyle=3     " tree view
let g:netrw_list_hide=netrw_gitignore#Hide()
let g:netrw_list_hide.=',\(^\|\s\s\)\zs\.\S\+'
