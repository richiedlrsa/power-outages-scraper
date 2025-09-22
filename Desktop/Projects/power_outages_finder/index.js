document.addEventListener('DOMContentLoaded', async () => {

    const provinceList = document.getElementById('province')
    const dataTable = document.getElementById('data-table')
    const LIMIT = 10
    const paginationUl = document.getElementById('pagination')

    async function fetchData() {
        try {
            const response = await fetch('https://power-outages-scraper.onrender.com/outages/')
            if (!response.ok) { throw new Error('Could not fetch data.') }
            return await response.json()
        } catch(error) {
            console.error(error)
            return []
          }
    }

    function processInitialData(outages) {
         // having a list of unique provinces allows us to create a dropdown of all available provinces for the user
        let provinces = new Set()
        // creating a province: sectors object allows us to dynamically populate the sectors based on the chosen province
        let provinceSectors = {}
        
        outages.forEach(outage => {
        if (!provinces.has(outage.province)) {
            let newProvince = document.createElement('option')
            newProvince.textContent = `${outage.province}`
            newProvince.value = `${outage.province.replace(' ', '-')}`
            newProvince.id = `${outage.province.toLowerCase().replace(' ', '-')}`
            provinceList.append(newProvince)
            provinces.add(outage.province)
        }
        if (!(outage.province in provinceSectors)) {
            provinceSectors[outage.province] =  new Set()
        }
        outage.maintenance.forEach(event => {
            event.sectors.forEach(sector => {
                provinceSectors[outage.province].add(sector.trim())
            })
        })
        }) 

        return provinceSectors
    }

    function populateSectors(provinceName, provinceSectors) {
        const sectorList = document.getElementById('sector-list')
        sectorList.innerHTML = ''

        if (provinceName && provinceSectors[provinceName]) {
            provinceSectors[provinceName].forEach(sector => {
            const newSector = document.createElement('option')
            newSector.value = sector.trim()
            sectorList.append(newSector)
            })
        }       
    }

    function queryData(params, outages, provinceSectors) {
        let page = params.get('page')
        // when the user first enters the page, there's no query parameter so we need to set a default page
        if (!page) { page = 1 }
        page = Number(page)
        let province = params.get('province')
        let sector = params.get('sector')
        let date = params.get('date')
        let company = params.get('company')

        if (company) {
            document.getElementById('selected-company').value = company
            document.getElementById('selected-company').textContent = company
            document.getElementById(`${company.toLowerCase()}`).remove()

            outages = outages.filter(outage => outage.company === company)
        }

        if (date) {
            document.getElementById('date').value = date
            outages = outages.filter(outage => outage.day === date)
        }

        if (province) {
            province = province.replace('-', ' ')
            populateSectors(province, provinceSectors)
            outages = outages.filter(outage => outage.province == province)
            document.getElementById(`${province.toLowerCase().replace(' ', '-')}`).remove()
            document.getElementById('selected-province').value = province.replace(' ', '-')
            document.getElementById('selected-province').textContent = province
            document.getElementById('title').textContent = `Mantenimientos Programados en ${province}`
        }

        if (sector) {
            document.getElementById('sector-input').setAttribute('value', sector)
            document.getElementById('title').textContent = `Mantenimientos Programados en ${sector}`

            outages = outages.filter(outage => {
                outage.maintenance = outage.maintenance.filter(maintenance => {
                    maintenance.sectors = maintenance.sectors.filter(s => s.trim() === sector)
                    return maintenance.sectors.length > 0
                })
                return outage.maintenance.length > 0
            })
        }

        createPagination(page, Math.ceil(outages.length / LIMIT))
        createDataTable(page, outages)
    }

    function createQueryString(page) {
        const newParams = new URLSearchParams(window.location.search)
        newParams.set('page', page)
        return `?${newParams.toString()}`
    }
    
    function createNextBtn(page, total_pages) {

        let nextBtn = document.createElement('li')
        let nextBtnLink = document.createElement('a')
        nextBtn.classList = 'page-item'
        nextBtnLink.classList = 'page-link'
        nextBtnLink.setAttribute('href', `${createQueryString(page + 1)}`)
        nextBtnLink.textContent = 'Siguiente'
        nextBtn.setAttribute('id', 'next-btn')
        nextBtn.append(nextBtnLink)
        if (total_pages === 0|| page === total_pages) { nextBtn.classList.add('disabled') }
        paginationUl.append(nextBtn)
    }

    function setActivePage(page) {
        let pageLi = document.getElementById(`page-${page}`)
        pageLi.classList.add('active')
        pageLi.querySelector('a').setAttribute('aria-current', 'page')
    }

    function createPagination(page, total_pages) {
        let prevBtn = document.getElementById('previous-btn')
        let prevBtnLink = prevBtn.querySelector('a')
        if (page === 1) { prevBtn.classList.add('disabled') }
        prevBtnLink.setAttribute('href', `${createQueryString(page - 1)}`)

        // each page will show all maintenance events for the first 10 provinces
        for (let i = 1; i <= total_pages; i++) {
            let newLi = document.createElement('li')
            let newA = document.createElement('a')
            newLi.classList = 'page-item'
            newLi.id = `page-${i}`
            newA.classList = 'page-link'
            newA.href = `${createQueryString(i)}`
            newA.textContent = `${i}`
            newLi.append(newA)
            paginationUl.append(newLi)
        }

        createNextBtn(page, total_pages)
        if (total_pages > 0) { setActivePage(page) }
    }

    function formatDate(date) {
        const dateObj = new Date(date)

        if (String(dateObj) === 'Invalid Date') { return date }

        const options = {
            weekday: 'long',
            day: 'numeric',
            month: 'long',
            year: 'numeric',
            timeZone: 'UTC' 
        }

        return dateObj.toLocaleDateString('es-ES', options)
    }

    function createDataTable(page, outages) {
        if (outages.length === 0) {
            const noResultsText = document.createElement('p')
            noResultsText.textContent = 'No se han encontrado resultados para esta busqueda.'
            dataTable.before(noResultsText)
        } else {
            let startIndex = (page - 1) * LIMIT
            let endIndex = page * LIMIT
            outages.slice(startIndex, endIndex).forEach(outage => {
                outage.maintenance.forEach(event => {
                    let newTr = document.createElement('tr')
                    let newTh = document.createElement('th')
                    let newProvinceTd = document.createElement('td')
                    let newDateTd = document.createElement('td')
                    let newTimeTd = document.createElement('td')
                    let newSectorTd = document.createElement('td')
                    newTh.scope = 'row'
                    newTh.textContent = `${outage.company}`
                    newProvinceTd.textContent = `${outage.province}`
                    newDateTd.textContent = `${formatDate(outage.day)}`     
                    newTimeTd.textContent = `${event.time}`
                    newSectorTd.textContent = `${event.sectors}`
                    newTr.append(newTh, newProvinceTd, newDateTd, newTimeTd, newSectorTd)
                    dataTable.append(newTr)
                })
            })
          }
    }

    async function init() {
        const outages = await fetchData()
        const provinceSectors = processInitialData(outages)
        const params = new URLSearchParams(window.location.search)

        queryData(params, structuredClone(outages), provinceSectors)

        provinceList.addEventListener('change', () => {
        provinceName = provinceList.options[provinceList.selectedIndex].text
        populateSectors(provinceName, provinceSectors)
        document.getElementById('sector-input').value = ''
        })

        document.getElementById('clear').addEventListener('click', () => {
            window.location.href = window.location.pathname
        })

    }

    init()
})