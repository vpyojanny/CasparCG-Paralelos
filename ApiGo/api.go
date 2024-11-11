package main

import (
	"fmt"
	"log"
	"net/http"

	"database/sql"

	"github.com/gin-gonic/gin"
	"github.com/go-sql-driver/mysql"
)

var db *sql.DB

// Configuración de la base de datos
func init() {
	var err error
	cfg := mysql.Config{
		User:   "root",
		Passwd: "VLsysadmin2024",
		Net:    "tcp",
		Addr:   "localhost:3306",
		DBName: "loteria",
	}
	db, err = sql.Open("mysql", cfg.FormatDSN())
	if err != nil {
		log.Fatal(err)
	}
	if err := db.Ping(); err != nil {
		log.Fatal(err)
	}
	fmt.Println("Conectado a la base de datos.")
}

// Estructura para los resultados de la lotería
type Resultado struct {
	Numero1 int    `json:"numero1"`
	Numero2 int    `json:"numero2"`
	Numero3 int    `json:"numero3"`
	Fecha   string `json:"fecha"`
}

// Endpoint para obtener el resultado actual de la lotería
func obtenerResultado(c *gin.Context) {
	nombreLoteria := c.Param("nombre")
	var resultado Resultado

	query := `SELECT numero1, numero2, numero3, fecha FROM resultados WHERE nombre_loteria = ? ORDER BY fecha DESC LIMIT 1`
	err := db.QueryRow(query, nombreLoteria).Scan(&resultado.Numero1, &resultado.Numero2, &resultado.Numero3, &resultado.Fecha)
	if err != nil {
		if err == sql.ErrNoRows {
			resultado = Resultado{Numero1: 29, Numero2: 31, Numero3: 27} // Valores predeterminados
		} else {
			log.Println("Error al obtener el resultado:", err)
		}
	}
	c.JSON(http.StatusOK, resultado)
}

// Endpoint para obtener el resultado anterior de la lotería
func obtenerResultadoAnterior(c *gin.Context) {
	nombreLoteria := c.Param("nombre")
	var resultado Resultado

	query := `SELECT numero1, numero2, numero3, fecha FROM resultados WHERE nombre_loteria = ? ORDER BY fecha DESC LIMIT 1 OFFSET 1`
	err := db.QueryRow(query, nombreLoteria).Scan(&resultado.Numero1, &resultado.Numero2, &resultado.Numero3, &resultado.Fecha)
	if err != nil {
		if err == sql.ErrNoRows {
			resultado = Resultado{Numero1: 0, Numero2: 0, Numero3: 0} // Valores predeterminados
		} else {
			log.Println("Error al obtener el resultado anterior:", err)
		}
	}
	c.JSON(http.StatusOK, resultado)
}

func main() {
	r := gin.Default()

	// Rutas
	r.GET("/api/loteria/:nombre", obtenerResultado)
	r.GET("/api/loteria/:nombre/anterior", obtenerResultadoAnterior)

	r.Run(":3000")
}
