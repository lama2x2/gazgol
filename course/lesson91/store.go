package lesson91

// Готовое хранилище в памяти. Его менять не нужно — используй в хендлерах.

import (
	"errors"
	"slices"
	"sync"
)

var ErrNotFound = errors.New("not found")

type Ad struct {
	ID    int    `json:"id"`
	Title string `json:"title"`
	Price int    `json:"price"`
}

type MemStore struct {
	mu     sync.Mutex
	ads    map[int]Ad
	nextID int
}

func NewMemStore() *MemStore {
	return &MemStore{ads: map[int]Ad{}, nextID: 1}
}

// Create сохраняет объявление и возвращает его с присвоенным ID.
func (s *MemStore) Create(title string, price int) Ad {
	s.mu.Lock()
	defer s.mu.Unlock()
	ad := Ad{ID: s.nextID, Title: title, Price: price}
	s.ads[ad.ID] = ad
	s.nextID++
	return ad
}

func (s *MemStore) Get(id int) (Ad, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	ad, ok := s.ads[id]
	if !ok {
		return Ad{}, ErrNotFound
	}
	return ad, nil
}

// List возвращает все объявления, отсортированные по ID.
func (s *MemStore) List() []Ad {
	s.mu.Lock()
	defer s.mu.Unlock()
	res := make([]Ad, 0, len(s.ads))
	for _, ad := range s.ads {
		res = append(res, ad)
	}
	slices.SortFunc(res, func(a, b Ad) int { return a.ID - b.ID })
	return res
}

func (s *MemStore) Delete(id int) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if _, ok := s.ads[id]; !ok {
		return ErrNotFound
	}
	delete(s.ads, id)
	return nil
}
