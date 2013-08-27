#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#include <sys/types.h>
#include <pcre.h>

#include <walk.h>
#include <pthread.h>
#include <time.h>

#include <iostream>
using namespace std;

#define OTL_ODBC // Compile OTL 4.0/ODBC
// The following #define is required with MyODBC 3.51.11 and higher
//#define OTL_ODBC_SELECT_STM_EXECUTE_BEFORE_DESCRIBE
#define OTL_ODBC_UNIX // uncomment this line if UnixODBC is used

#include <otlv4.h>

#define TEST_DB
//#define USE_PCRE
#define PROCESS_THREAD_NO 	8

//const char* gcov_path   = "/home/thomas/gcov_log";
//const char* db_conn_str = "ats/ats@atsdb";
const char* gcov_path   = "/root/work/gcov_log";
const char* db_conn_str = "root/root@testdsn";

int add_src_line(db_load_info *db_load, gcov_file_info *gcov_head, int len);


static list_info *gcov_list = NULL;
void parse_init(int len)
{
	
	list_info *head = (list_info *)malloc(sizeof(list_info));
	head->count = 0;
	head->max = len;
	head->node = (name_info *)malloc(sizeof(name_info) * len);
	memset(head->node, 0, sizeof(name_info) * len);
	gcov_list = head;
}

int get_gcov_file_no(const char *path) 
{
	DIR              *pDir ;
	struct dirent    *ent  ;
	char              childpath[512];
	//int gcov_count = 0;

#ifdef USE_PCRE
	pcre *p_pcre;
	const char *pattern = ".*.gcov$";
	const char *p_error_msg = NULL;
	int n_offset = -1;
	if (NULL == (p_pcre = pcre_compile(pattern, 0, &p_error_msg, &n_offset, NULL)))
	{
		printf("ErrorMsg: %s, Offset = %d\n", p_error_msg, n_offset);
		return -1;
	}
#else
	char p_last_point = '.';
	const char *gcov_tail = "gcov";
#endif
	
	pDir=opendir(path);
	if(!pDir){
		printf("open %s failed \n", path);
		exit(1);
	}
	memset(childpath,0,sizeof(childpath));

	while((ent=readdir(pDir))!=NULL)
	{
		if(strcmp(ent->d_name, ".") == 0 || strcmp(ent->d_name, "..") == 0)
			continue;
		else {
			sprintf(childpath, "%s/%s", path, ent->d_name);
			if(ent->d_type & DT_DIR) {
				get_gcov_file_no(childpath);
			}
			else if(ent->d_type & DT_REG) {
			#ifdef USE_PCRE
				if(pcre_exec(p_pcre, NULL, childpath, strlen(childpath), 0, 0, NULL, 0) < 0)
				{

				}
				else // matched
				{
					gcov_count++;
				}
			#else
				char *p_point = NULL;
				int ret;
				p_point = strrchr(childpath, p_last_point);
				if(p_point) {
					ret = strncmp(p_point+1, gcov_tail, 4);
					if(ret == 0) {// matched
						gcov_count++;
					}
				}
			#endif

			}
		}

	}

	return 0;
}

void listDir(const char *path)
{
	DIR              *pDir;
	struct dirent    *ent;
	char              childpath[512];

#ifdef USE_PCRE
	pcre *p_pcre;
	const char *pattern = ".*.gcov$";
	const char *p_error_msg = NULL;
	int n_offset = -1;
	if (NULL == (p_pcre = pcre_compile(pattern, 0, &p_error_msg, &n_offset, NULL)))
	{
		printf("ErrorMsg: %s, Offset = %d\n", p_error_msg, n_offset);
		return;
	}
#else
	// don't use pcre, but string process function
	char p_last_point = '.';
	const char *gcov_tail = "gcov";
#endif
	pDir=opendir(path);
	memset(childpath,0,sizeof(childpath));

	while((ent=readdir(pDir))!=NULL)
	{
		if(strcmp(ent->d_name, ".") == 0 || strcmp(ent->d_name, "..") == 0)
			continue;
		else {
			sprintf(childpath, "%s/%s", path, ent->d_name);
			if(ent->d_type & DT_DIR) {
				listDir(childpath);
			}
			else if(ent->d_type & DT_REG) {
			#ifdef USE_PCRE
				if(pcre_exec(p_pcre, NULL, childpath, strlen(childpath), 0, 0, NULL, 0) < 0)
				{
					//printf("nomatch : \n");
				}
				else // matched
				{ 
					name_info *name_head = gcov_list->node;
					name_info *p_curr = name_head+(gcov_list->count);
					snprintf(p_curr->name, BUF_SIZE, "%s", childpath);
					gcov_list->count++;

					gcov_count++;
				}
			#else
				char *p_point = NULL;
				int ret;
				p_point = strrchr(childpath, p_last_point);
				if(p_point) {
					ret = strncmp(p_point+1, gcov_tail, 4);
					if(ret == 0) {// matched
						name_info *name_head = gcov_list->node;
						name_info *p_curr = name_head+(gcov_list->count);
						snprintf(p_curr->name, BUF_SIZE, "%s", childpath);
						gcov_list->count++;
						gcov_count++;
					}
				}
			#endif
			}
		}

	}
	//printf("\n\ngcov file number is %d\n", gcov_count);

}

void get_base_name(char *path, char *dest)
{
	char chr = '/';

	char *p_name = strrchr(path, chr);
	snprintf(dest, strlen(p_name)-5, "%s", p_name+1);
	
}

void print_list()
{
	int i; 
	printf("gcov_list max is %d\n", gcov_list->max);
	printf("gcov_list count is %d\n", gcov_list->count);
	
	for(i=0; i<=gcov_list->count; i++) {
		//name_info *p_head = gcov_list->node;
		//name_info *p_curr = p_head+i;
		//printf("%s\n", p_curr->name);
		//get_base_name(p_curr->name);
	}
}

int parse_file(gcov_file_info *p_gcov)
{
	//TODOs
	// parse file according to the format xx:xx:xx
	FILE *fp;
	fp = fopen(p_gcov->path, "r");
	char line[256] = {0};
	
	if(!fp) {
		printf("open %s failed\n", p_gcov->path);
		return 1;
	}

	const char *delims = ":";
	char *result1 = NULL;
	char *result2 = NULL;
	char *save_ptr = NULL;

	int run_no, line_no;
	cover_record *p_curr_cov = NULL;
	
	while(fgets(line, sizeof(line), fp)) {
		result1 = strtok_r(line, delims, &save_ptr);
		result2 = strtok_r(NULL, delims, &save_ptr);
		if (result1 == NULL) 
			continue;
		if ((run_no = atoi(result1)) == 0)
			continue;
		if (result2 == NULL)
			continue;
		if ((line_no = atoi(result2)) == 0)
			continue;

		p_curr_cov = p_gcov->cover_head;
		if(p_gcov->count < GCOV_MAX_LINE_NO){
			//p_curr = p_gcov->cover_head+p_gcov->count;
			p_curr_cov += p_gcov->count;
			p_curr_cov->line = line_no;
			p_curr_cov->run_no = run_no;
				
			p_gcov->count++;
			
			if(p_curr_cov->line == 0 || p_curr_cov->run_no == 0) {
				printf("XXXXXX%s, line_no = %d, run_no = %d\n", p_gcov->path, line_no, run_no);
			}
		}
		else {
			//TODOs
			printf("CRASH: There has a huge source file : %s\n", p_gcov->path);
			exit(1);
		}		
	}
	fclose(fp);
	return 0;
	
}

void check_valid(gcov_file_info *head, int len)
{
	cover_record *p_cov_head = NULL;
	cover_record *p_cov_curr = NULL;
	for(int i=0; i<len; i++) {
		gcov_file_info *p_curr = head+i;
		p_cov_head = p_curr->cover_head;
		if(p_curr->count > 0) {
			for(int j=0; j<p_curr->count; j++) {
				p_cov_curr = p_cov_head+j;
				if(p_cov_curr->line == 0 || p_cov_curr->run_no == 0) {
					printf("%s, line = %d, run = %d, total = %d\n", 
						p_curr->path, p_cov_curr->line, p_cov_curr->run_no, p_curr->count);
					break;
				}
			}
		}
		
	}
}


/**
  *   purpose: parse file by multiple-thread
  *
  */
void *parse_process(void *args)
{
	param_t *param = (param_t *)args;
	name_info *head = param->p_node;
	int len = param->length;

	printf("In thread %d, len = %d\n", param->no, len);
	
	gcov_file_info *p_gcov_head = NULL;
	p_gcov_head = (gcov_file_info *)malloc(len * sizeof(gcov_file_info));
	memset(p_gcov_head, 0, len*sizeof(gcov_file_info));
	
	for(int i=0; i<len; i++) {
		//p_curr_name = head+i;
		gcov_file_info *gcov_node = p_gcov_head+i;
		
		snprintf(gcov_node->path, sizeof(gcov_node->path), "%s", (head+i)->name);
		get_base_name(gcov_node->path, gcov_node->filename);
		gcov_node->cover_head = (cover_record *)malloc(sizeof(cover_record) * GCOV_MAX_LINE_NO);
		memset(gcov_node->cover_head, 0, sizeof(cover_record) * GCOV_MAX_LINE_NO);
		parse_file(gcov_node);
	}

	check_valid(p_gcov_head, len);

	time_t now;
	time(&now);
	printf("Thread %d parse finished, begin to into db %s\n", param->no, ctime(&now));
	#ifdef TEST_DB
	db_load_info *db_load = param->db_info;
	add_src_line(db_load, p_gcov_head, len);

	time(&now);
	printf("Thread %d into db finished: %s\n", param->no, ctime(&now));
	#endif
	return NULL;
}



// read the list, which record all gcov file name. Then start multi-threads to process the gcov files
int start_thread(db_load_info *db_info)
{
	pthread_t thd[PROCESS_THREAD_NO];

	int each_len = gcov_list->count/PROCESS_THREAD_NO;
	int mode_len = gcov_list->count % PROCESS_THREAD_NO;
	name_info *p_curr = gcov_list->node;
	int i;
	void *join_status;
	
	for (i=0; i<PROCESS_THREAD_NO; i++) {
		param_t param[PROCESS_THREAD_NO];
		param[i].p_node = p_curr + (each_len*i);
		if(i == PROCESS_THREAD_NO-1)
			param[i].length = each_len+mode_len;
		else
			param[i].length = each_len;
		param[i].no = i;
		param[i].db_info = db_info;
		pthread_create(&thd[i], NULL, parse_process, &param[i]);
	}

	for(i=0; i<PROCESS_THREAD_NO; i++) {
		pthread_join(thd[i], &join_status);
	}

	return 0;
	
}


int add_load(db_load_info &load_info)
{
	static char const add_load[] =
		"insert into db_offical_load(ats_load_name, ats_timestamp) "
		"values(:load_name<char[128]>, now()) ";
	static char const get_load[] =
		"select id from db_offical_load where ats_load_name = :load_name<char[128]>";

	static char const get_max_load[] = 
		"select ats_load_name from db_offical_load where id = (select max(id) from db_offical_load)";
	
	otl_connect db;
	int load_id;

	otl_connect::otl_initialize(); // initialize the database API environment  
    try{
		db.rlogon(db_conn_str);// connect to the database  

		char load_name[256];
		otl_stream os_max(1, get_max_load, db);
		if(!os_max.eof()){
			//::std::string load_name;
			
			os_max>>load_name;
			char *p_end = strrchr(load_name, '_');
			char buf[10];
			snprintf(buf, sizeof(buf), "%s", p_end+1);
			int no = atoi(buf);
				if(no != 0){
				no++;
				snprintf(p_end+1, sizeof(buf), "%d", no);
			}
			else {
				printf("parse string failed \n");
				exit(1);
			}
			//cout<<load_name<<endl;
			printf("%s\n", load_name);
		}

		otl_stream os_add(1, add_load, db);
		os_add<<load_name;
		
		otl_stream os_get(1, get_load, db);
		os_get<<load_name;
		os_get>>load_id;
		cout<<load_id<<endl;
		load_info.load_id = load_id;
		snprintf(load_info.load_name, sizeof(load_info.load_name), "%s", load_name);
		
	}
   
    catch(otl_exception&p){ // intercept OTL exceptions  
        cerr<<p.msg<<endl; // print out error message  
        cerr<<p.stm_text<<endl; // print out SQL that caused the error  
        cerr<<p.var_info<<endl; // print out the variable that caused the error  
	}
   
    db.logoff();

	return 0;
}

int add_case(db_load_info &db_load)
{
	const char *case_id = "100010";
	
	static char const add_case[] = 
		"insert into db_rts_case(ats_case_id, ats_load_name, ats_load_fk_id, ats_timestamp) "
		"values(:case_id<char[128]>, :load_name<char[256]>, :load_id<int>, now())";

	static char const get_case[] = 
		"select id from db_rts_case where ats_load_fk_id=:load_id<int>";

	otl_connect db;
	otl_connect::otl_initialize(); // initialize the database API environment  
    try{
		db.rlogon(db_conn_str);// connect to the database  

		otl_stream os_add(1, add_case, db);
		os_add<<case_id<<db_load.load_name<<db_load.load_id;

		otl_stream os_get(1, get_case, db);
		os_get<<db_load.load_id;
		if(!os_get.eof()) {
			os_get>>db_load.case_id;
			snprintf(db_load.case_name, sizeof(db_load.case_name), "%s", case_id);
		}
	}
   
    catch(otl_exception&p){ // intercept OTL exceptions  
        cerr<<p.msg<<endl; // print out error message  
        cerr<<p.stm_text<<endl; // print out SQL that caused the error  
        cerr<<p.var_info<<endl; // print out the variable that caused the error  
	}
   
    db.logoff();

	return 0;
}


int add_src_line(db_load_info *db_load, gcov_file_info *gcov_head, int len)
{
	static char const add_src[] = 
		"insert into db_src_file(ats_case_fk_id, ats_load_name, ats_case_id, "
		"ats_path_name, ats_src_name, ats_timestamp) "
		"values(:case_fk_id<int>, :load_name<char[256]>, :case_name<char[256]>, "
		":path_name<char[256]>, :ats_src_name<char[256]>, now())";

	static char const get_src[] = 
		"select id from db_src_file where ats_path_name = :path_name<char[256]> and ats_case_fk_id = :case_id<int>";

	static char const add_line[] = 
		"insert into db_line_executed(ats_src_file_fk_id, ats_load_name, ats_case_id, ats_path_name, "
		"ats_line_num, ats_exec_count, ats_timestamp) "
		"values(:src_id<int>, :load_name<char[256]>, :case_name<char[256]>, :path_name<char[256]>, "
		":line_no<int>, :exec_count<int>, now())";

	otl_connect db;
	otl_connect::otl_initialize(); // initialize the database API environment  
	gcov_file_info *p_gcov_file_curr = NULL;
	
    try{
		db.rlogon(db_conn_str);// connect to the database  

		otl_stream os_add_src(1, add_src, db);
		os_add_src.set_commit(0);
		for(int i=0; i<len; i++){
			p_gcov_file_curr = gcov_head+i;
			// add src files
			os_add_src<<db_load->case_id<<db_load->load_name<<db_load->case_name
				<<p_gcov_file_curr->path<<p_gcov_file_curr->filename;

			//printf("get src: path_name = %s, case_id: = %d\n",(gcov_head+i)->path, db_load->case_id);
			int src_id;
			otl_stream os_get_src(1, get_src, db);
			os_get_src.set_commit(0);
			os_get_src<<p_gcov_file_curr->path<<db_load->case_id;
			
			if(!os_get_src.eof()) {
				os_get_src>>src_id;
				
				cover_record *cov_head = p_gcov_file_curr->cover_head;
				otl_stream os_add_line(1, add_line, db);
				os_add_line.set_commit(0);
				for(int j=0; j<p_gcov_file_curr->count; j++){
					
					if(p_gcov_file_curr->count == 0){
						continue;
					}
					/**
					printf("load_name: %s, case_name: %s src_id: %d path: %s, %d:%d\n", 
						db_load->load_name, db_load->case_name, src_id, (gcov_head+i)->path, 
						(cov_head+j)->line, (cov_head+j)->run_no);*/
					try{
					os_add_line<<src_id<<db_load->load_name<<db_load->case_name
						<<p_gcov_file_curr->path<<(cov_head+j)->line<<(cov_head+j)->run_no;
					}
					catch(otl_exception& p) {
						cerr<<p.msg<<endl;
						#if 0
						printf("gcov count %d\n",(gcov_head+i)->count);
						printf("--->load_name: %s, case_name: %s src_id: %d path: %s, %d:%d\n", 
						db_load->load_name, db_load->case_name, src_id, (gcov_head+i)->path, 
						(cov_head+j)->line, (cov_head+j)->run_no); 
						#endif
						CRASH_HERE("count=%d, load_name: %s, case_name: %s src_id: %d path: %s, %d:%d\n", 
							p_gcov_file_curr->count, db_load->load_name, db_load->case_name, src_id, 
							p_gcov_file_curr->path, (cov_head+j)->line, (cov_head+j)->run_no);
					}
				}
			}
		}
		db.commit();
	}
   
    catch(otl_exception&p){ // intercept OTL exceptions  
        cerr<<p.msg<<endl; // print out error message  
        cerr<<p.stm_text<<endl; // print out SQL that caused the error  
        cerr<<p.var_info<<endl; // print out the variable that caused the error  
	}
   
    db.logoff();

	return 0;	
}

int main(int argc,char *argv[])
{
	//std::string load_name = "load_3";

	time_t now;
	time(&now);
	printf("%s\n",ctime(&now));
	
	db_load_info db_load;
	#ifdef TEST_DB
	add_load(db_load);
	add_case(db_load);
	#endif
	
	if(get_gcov_file_no(gcov_path)){
		printf("get gcov file no failed\n");
		exit(1);
	}

	parse_init(gcov_count);
	listDir(gcov_path);
	start_thread(&db_load);
	//print_list();

	time(&now);
	printf("%s\n", ctime(&now));
	
	return 0;
}
